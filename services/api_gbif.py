import requests

def get_species_info(species_name):
    try:
        response = requests.get(
            f"https://api.gbif.org/v1/species/match?name={species_name}"
        )
        response.raise_for_status()
        data = response.json()

        if "usageKey" not in data:
            return {
                "taxonomy": "Unknown",
                "region": "Unknown"
            }

        usage_key = data["usageKey"]

        # Now fetch full species info
        response = requests.get(f"https://api.gbif.org/v1/species/{usage_key}")
        response.raise_for_status()
        full_data = response.json()

        taxonomy = {
            "kingdom": full_data.get("kingdom"),
            "phylum": full_data.get("phylum"),
            "class": full_data.get("class"),
            "order": full_data.get("order"),
            "family": full_data.get("family"),
            "genus": full_data.get("genus"),
            "species": full_data.get("species")
        }

        # You can fetch distribution too (regions)
        dist_response = requests.get(f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&limit=1")
        dist_response.raise_for_status()
        dist_data = dist_response.json()

        region = "Unknown"
        if dist_data["results"]:
            region = dist_data["results"][0].get("country", "Unknown")

        return {
            "taxonomy": taxonomy,
            "region": region
        }

    except Exception as e:
        return {
            "taxonomy": "Error fetching taxonomy",
            "region": "Error fetching region",
            "error": str(e)
        }
