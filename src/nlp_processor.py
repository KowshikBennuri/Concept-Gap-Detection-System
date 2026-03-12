import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

class NLPProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def clean_text(self, text):
        # Remove punctuation and lowercase everything
        text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
        tokens = word_tokenize(text)
        # Remove "um", "the", "is" and convert words to base form (e.g., paging -> page)
        cleaned = [self.lemmatizer.lemmatize(w) for w in tokens if w not in self.stop_words]
        return " ".join(cleaned)

    def extract_matches(self, student_text, target_keywords):
        # Check which knowledge base keywords are in the student speech
        student_text_lower = student_text.lower()
        covered = [kw for kw in target_keywords if kw.lower() in student_text_lower]
        missing = [kw for kw in target_keywords if kw.lower() not in student_text_lower]
        return covered, missing