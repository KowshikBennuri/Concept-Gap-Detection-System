from sentence_transformers import SentenceTransformer, util

class SimilarityAnalyzer:
    def __init__(self):
        # Updated to the high-accuracy research model
        self.model = SentenceTransformer('all-mpnet-base-v2')

    def get_similarity_score(self, student_text, ideal_text):
        emb1 = self.model.encode(student_text, convert_to_tensor=True)
        emb2 = self.model.encode(ideal_text, convert_to_tensor=True)
        return util.cos_sim(emb1, emb2).item()