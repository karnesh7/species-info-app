import unittest
from services.report_generator import generate_markdown_dossier

class TestReportGenerator(unittest.TestCase):
    def test_markdown_dossier_generation(self):
        sample_data = {
            "common_name": "Bengal Tiger",
            "scientific_name": "Panthera tigris tigris",
            "category": "Mammal",
            "iucn_status": {
                "code": "EN",
                "category": "ENDANGERED",
                "iucn_url": "https://www.iucnredlist.org/species/15955"
            },
            "taxonomy": {
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "class": "Mammalia",
                "order": "Carnivora",
                "family": "Felidae",
                "genus": "Panthera",
                "species": "Panthera tigris"
            },
            "regions": ["India", "Bangladesh", "Nepal"],
            "synonyms": ["Felis tigris"],
            "wikipedia": {
                "summary": "The Bengal tiger is a population of the Panthera tigris tigris subspecies native to the Indian subcontinent.",
                "url": "https://en.wikipedia.org/wiki/Bengal_tiger",
                "sections": {
                    "Characteristics": "The Bengal tiger's coat is yellow to light orange..."
                }
            },
            "model_scores": [
                {"label": "Panthera tigris", "score": 0.96}
            ]
        }

        md_output = generate_markdown_dossier(sample_data)
        self.assertIn("# Biological Specimen Field Dossier: Bengal Tiger", md_output)
        self.assertIn("*Panthera tigris tigris*", md_output)
        self.assertIn("ENDANGERED (EN)", md_output)
        self.assertIn("Animalia", md_output)
        self.assertIn("Characteristics", md_output)
        self.assertIn("https://www.iucnredlist.org/species/15955", md_output)

if __name__ == "__main__":
    unittest.main()
