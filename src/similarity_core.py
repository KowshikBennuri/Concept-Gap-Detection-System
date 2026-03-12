from sentence_transformers import SentenceTransformer, util

class SimilarityAnalyzer:
    def __init__(self):
        # This downloads a lightweight AI model on first run
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_similarity_score(self, student_text, ideal_text):
        # Convert sentences into mathematical vectors (embeddings)
        emb1 = self.model.encode(student_text, convert_to_tensor=True)
        emb2 = self.model.encode(ideal_text, convert_to_tensor=True)
        # Calculate the 'cosine similarity' (0.0 to 1.0)
        return util.cos_sim(emb1, emb2).item()