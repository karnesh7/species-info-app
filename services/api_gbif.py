import requests

def get_species_info(scientific_name):
    # Mock response for now
    return {
        "taxonomy": {"kingdom": "Animalia", "phylum": "Chordata"},
        "region": "Africa"
    }

# Later replace with actual GBIF API call
