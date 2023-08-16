import torch
import torch.nn as nn
from transformers import BertConfig
from kobert_transformers import get_tokenizer
from kobert_transformers import get_kobert_model
from transformers import BertPreTrainedModel
from .newsCleaner import NewsCleaner


class BertSumExt:
    def __init__(self, model_path='KoBertSumExt/kobert_ext_15365.pth'):
        self.model = self.load_model(model_path)
        self.tokenizer = get_tokenizer()
        self.cleaner = NewsCleaner()

    def __call__(self, text):
        return self.extract_summary(text)

    def extract_summary(self, text, summary_length=3):
        sentences = self.cleaner.apply(text)

        data = self.make_dataset(sentences)
        input = data['input']
        articles = data['articles']

        output = self.model(**input)
        cls_token = output['logits']

        summary = []

        softmax_logit = torch.softmax(cls_token.view(-1), dim=0).view(-1)

        _, sum_idxs = torch.topk(softmax_logit, min(summary_length, softmax_logit.shape[-1]))
        sum_idxs = sorted(sum_idxs.tolist())

        for sum_idx in sum_idxs:
            summary.append(articles[sum_idx])

        return "\n".join(summary)

    def make_dataset(self, articles, max_seq_len=512):

        cls_token_id = self.tokenizer.cls_token_id  # [CLS]
        sep_token_id = self.tokenizer.sep_token_id  # [SEP]
        pad_token_id = self.tokenizer.pad_token_id  # [PAD]

        # Data Initialization
        index_of_words = []
        token_type_ids = []
        cls_mask = []
        token_num = 0
        token_type_state = False

        for idx in range(len(articles)):
            article = articles[idx]
            tmp_index = self.tokenizer.encode(article, add_special_tokens=False)
            num_tmp_index = len(tmp_index) + 2

            if token_num + num_tmp_index <= max_seq_len:
                index_of_words += [cls_token_id] + tmp_index + [sep_token_id]
                token_type_ids += [int(token_type_state)] * num_tmp_index
                cls_mask += [True] + [False] * (num_tmp_index - 1)

                token_num += num_tmp_index
                token_type_state = not token_type_state

            if token_num + num_tmp_index > max_seq_len or idx == len(articles) - 1:
                # attention mask
                attention_mask = [1] * token_num

                # Padding Length
                padding_length = max_seq_len - token_num

                # Padding
                index_of_words += [pad_token_id] * padding_length  # [PAD] padding
                token_type_ids += [token_type_state] * padding_length  # last token_type_state padding
                attention_mask += [0] * padding_length  # zero padding
                cls_mask += [False] * padding_length

                input = {
                    'input_ids': torch.tensor([index_of_words]),
                    'token_type_ids': torch.tensor([token_type_ids]),
                    'attention_mask': torch.tensor([attention_mask]),
                    'cls_mask': torch.tensor([cls_mask])
                }
                data = {
                    "id": id,
                    "input": input,
                    "articles": articles
                }

                return data

    def load_model(self, ckpt_path):
        ctx = "cuda" if torch.cuda.is_available() else "cpu"
        device = torch.device(ctx)

        checkpoint = torch.load(ckpt_path, map_location=device)
        model = KoBertSumExt()
        model.load_state_dict(checkpoint['model_state_dict'])

        return model


class KoBertSumExt(BertPreTrainedModel):
  def __init__(self,
                hidden_size = 768,
                hidden_dropout_prob = 0.1,
               ):
    super().__init__(get_kobert_config())

    self.kobert = get_kobert_model()

    self.dropout = nn.Dropout(hidden_dropout_prob)
    self.ffn = nn.Linear(hidden_size, 4*hidden_size)
    self.classifier = nn.Linear(4*hidden_size, 1)

    self.init_weights()

  def forward(
          self,
          input_ids=None,
          attention_mask=None,
          token_type_ids=None,
          labels=None,
          cls_mask=None
          ):
    outputs = self.kobert(
      input_ids,
      attention_mask=attention_mask,
      token_type_ids=token_type_ids,
    )

    logits = outputs.last_hidden_state

    # 레이어 부분
    logits = self.dropout(logits)
    logits = self.ffn(logits)
    logits = self.classifier(logits)
    ##

    active_logits = logits[cls_mask]

    loss = None
    if labels is not None:
      active_labels = labels[cls_mask]

      pos_weight = torch.sum(active_labels == 0)/ torch.sum(active_labels == 1)
      loss_fct = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

      loss = loss_fct(active_logits.view(-1), active_labels.view(-1))

    return_data ={
      'loss':loss,
      'logits':active_logits
    }
    return return_data


def get_kobert_config():
    kobert_config = {
        'attention_probs_dropout_prob': 0.1,
        'hidden_act': 'gelu',
        'hidden_dropout_prob': 0.1,
        'hidden_size': 768,
        'initializer_range': 0.02,
        'intermediate_size': 3072,
        'max_position_embeddings': 512,
        'num_attention_heads': 12,
        'num_hidden_layers': 12,
        'vocab_size': 8002
    }
    return BertConfig.from_dict(kobert_config)
