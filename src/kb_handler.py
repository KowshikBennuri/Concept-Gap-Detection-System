import json

class KnowledgeBase:
    def __init__(self, file_path='data/knowledge_base.json'):
        # Open and load the JSON file you created
        with open(file_path, 'r') as f:
            self.data = json.load(f)

    def get_all_concepts(self):
        # Returns a list of all concept names for the UI dropdown
        return [item['concept_name'] for item in self.data]

    def get_concept_details(self, concept_name):
        # Finds the specific concept data (keywords/ideal answer)
        for item in self.data:
            if item['concept_name'].lower() == concept_name.lower():
                return item
        return None