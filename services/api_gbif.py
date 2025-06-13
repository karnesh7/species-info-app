import requests

def mock_gbif_call(species_name):
    url = f"https://api.gbif.org/v1/species/match?name={species_name}"
    response = requests.get(url)
    print(f"GBIF response: {response.status_code}")
    # Mock return
    return {"taxonomy": {"kingdom": "Animalia"}, "region": "Africa"}
