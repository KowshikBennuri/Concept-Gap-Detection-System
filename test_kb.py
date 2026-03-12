from src.kb_handler import KnowledgeBase

kb = KnowledgeBase()
concepts = kb.get_all_concepts()
print(f"Concepts found: {concepts}")
# Verify we can pull 'Paging' specifically
print(f"Paging Keywords: {kb.get_concept_details('Paging')['keywords']}")