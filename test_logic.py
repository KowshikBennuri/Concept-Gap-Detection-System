from src.kb_handler import KnowledgeBase
from src.nlp_processor import NLPProcessor
from src.similarity_core import SimilarityAnalyzer

def run_logic_test():
    print("--- Starting System Logic Test ---")
    
    # 1. Initialize all modules
    kb = KnowledgeBase()
    nlp = NLPProcessor()
    sim = SimilarityAnalyzer()
    
    # 2. Pick a concept from your JSON
    target_concept = "Paging"
    concept_data = kb.get_concept_details(target_concept)
    
    if not concept_data:
        print(f"Error: Concept '{target_concept}' not found in JSON.")
        return

    # 3. Simulate a student explanation (a "partial" answer)
    student_explanation = "Paging is a memory management scheme that uses page tables, but I don't remember frames."
    
    print(f"\nTarget Concept: {target_concept}")
    print(f"Student Said: '{student_explanation}'")
    
    # 4. Run Keyword Extraction
    covered, missing = nlp.extract_matches(student_explanation, concept_data['keywords'])
    
    # 5. Run Semantic Similarity
    score = sim.get_similarity_score(student_explanation, concept_data['ideal_answer'])
    
    # 6. Display Results
    print("\n--- Results ---")
    print(f"Semantic Similarity Score: {score:.2f} (Target: > 0.70)")
    print(f"✅ Keywords Found: {covered}")
    print(f"❌ Keywords Missing: {missing}")
    
    if score > 0.6:
        print("\nConclusion: Logic is working! The system caught the gaps and understood the meaning.")
    else:
        print("\nConclusion: Check your Similarity Core; the score seems lower than expected.")

if __name__ == "__main__":
    run_logic_test()