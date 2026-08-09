import evaluate
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch

class ConceptEvaluator:
    """
    Ensemble evaluation engine providing comparative analysis across 
    statistical (TF-IDF), deep learning (Transformers), and NLP research metrics.
    """
    def __init__(self):
        # Deep Learning Ensemble
        self.models = {
            "MiniLM": SentenceTransformer('all-MiniLM-L6-v2'),
            "MPNET": SentenceTransformer('all-mpnet-base-v2'),
            "RoBERTa": SentenceTransformer('all-distilroberta-v1')
        }
        
        # NLP Research Standards
        self.rouge = evaluate.load("rouge")
        self.bertscore = evaluate.load("bertscore")

    def _tfidf_cosine(self, transcript, ideal_answer):
        """
        Non-Deep Learning lexical baseline using traditional vector space modeling.
        """
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        vectors = vectorizer.fit_transform([transcript, ideal_answer])
        return float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])

    def get_comparative_scores(self, transcript, ideal_answer):
        """
        Calculates a comprehensive metric suite for academic comparative study.
        """
        scores = {}
        
        # 1. Deep Learning Model Competition
        for name, model in self.models.items():
            emb1 = model.encode(transcript, convert_to_tensor=True)
            emb2 = model.encode(ideal_answer, convert_to_tensor=True)
            scores[f"{name.lower()}_score"] = float(util.pytorch_cos_sim(emb1, emb2)[0][0])

        # 2. Statistical Baseline
        scores["tfidf_score"] = self._tfidf_cosine(transcript, ideal_answer)

        # 3. ROUGE Suite - EXPLICIT KEY MAPPING
        rouge_results = self.rouge.compute(predictions=[transcript], references=[ideal_answer])
        
        # We manually map them to ensure they match your 'app.py' print statements and SQL
        # The evaluate library usually returns them as 'rouge1', 'rouge2', 'rougeL'
        scores["rouge1"] = rouge_results["rouge1"]
        scores["rouge2"] = rouge_results["rouge2"]
        scores["rouge_l"] = rouge_results["rougeL"] # Map rougeL to rouge_l
        
        # 4. BERTScore
        bert_results = self.bertscore.compute(predictions=[transcript], references=[ideal_answer], lang="en")
        scores["bert_score"] = bert_results["f1"][0]
        
        return scores