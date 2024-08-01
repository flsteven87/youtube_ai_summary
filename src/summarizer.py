import os
import torch
from transformers import BertModel, BertTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI()

# BERT Extractive Summarization
class BertSummarizer:
    def __init__(self, model_name="bert-base-chinese"):
        self.model = BertModel.from_pretrained(model_name)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model.eval()

    def summarize(self, text, num_sentences=3):
        sentences = text.split('。')
        embeddings = self._get_embeddings(sentences)
        sentence_scores = self._get_sentence_scores(embeddings)
        summary = self._get_summary(sentences, sentence_scores, num_sentences)
        return summary

    def _get_embeddings(self, sentences):
        embeddings = []
        for sentence in sentences:
            inputs = self.tokenizer(sentence, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
            embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
        return np.array(embeddings)

    def _get_sentence_scores(self, embeddings):
        centroid = embeddings.mean(axis=0)
        scores = cosine_similarity([centroid], embeddings)[0]
        return scores

    def _get_summary(self, sentences, scores, num_sentences):
        ranked_sentences = [sentences[i] for i in np.argsort(scores)[-num_sentences:]]
        return '。'.join(ranked_sentences)

# OpenAI GPT-4 Summarization
openai.api_key = OPENAI_API_KEY

def summarize_with_gpt4(text):

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "請以繁體中文總結以下文本：\n" + text},    
        ],
    temperature=0.7
    )

    summary = response.choices[0].message.content
    return summary
