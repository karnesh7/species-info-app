import requests

def mock_inaturalist_call(image_path):
    url = "https://api.inaturalist.org/v1/identifications"
    files = {'file': open(image_path, 'rb')}
    response = requests.post(url, files=files)
    # Just show status code for now
    print(f"iNaturalist response: {response.status_code}")
    # Mock return (real API needs token + correct endpoint)
    return {"scientific_name": "Panthera leo", "category": "Mammal"}
