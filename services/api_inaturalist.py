import requests

def get_scientific_name_from_common(common_name):
    url = f"https://api.inaturalist.org/v1/search?q={common_name}&sources=taxa"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for result in data.get("results", []):
            record = result.get("record", {})
            if record.get("rank") == "species":
                return record.get("name")  # scientific name
        return None
    except Exception as e:
        print(f"Error fetching scientific name: {e}")
        return None

def get_common_name(scientific_name):
    url = f"https://api.inaturalist.org/v1/taxa?q={scientific_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for result in data.get("results", []):
            if result.get("name", "").lower() == scientific_name.lower():
                return result.get("preferred_common_name")
        return None
    except Exception as e:
        print(f"Error fetching common name: {e}")
        return None