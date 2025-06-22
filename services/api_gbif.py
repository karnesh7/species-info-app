import requests

def get_species_info(species_name):
    try:
        # Step 1: Match species name to get GBIF usageKey
        match_response = requests.get(
            f"https://api.gbif.org/v1/species/match?name={species_name}"
        )
        match_response.raise_for_status()
        match_data = match_response.json()

        if "usageKey" not in match_data:
            return {
                "taxonomy": "Unknown",
                "regions": [],
                "synonyms": [],
                "habitats": []
            }

        usage_key = match_data["usageKey"]

        # Step 2: Get full species data
        species_response = requests.get(f"https://api.gbif.org/v1/species/{usage_key}")
        species_response.raise_for_status()
        species_data = species_response.json()

        taxonomy = {
            "kingdom": species_data.get("kingdom"),
            "phylum": species_data.get("phylum"),
            "class": species_data.get("class"),
            "order": species_data.get("order"),
            "family": species_data.get("family"),
            "genus": species_data.get("genus"),
            "species": species_data.get("species")
        }

        # Step 3: Get top regions from occurrence facets
        facet_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&facet=country&facetLimit=10&limit=0"
        facet_response = requests.get(facet_url)
        facet_response.raise_for_status()
        facet_data = facet_response.json()

        regions = []
        if facet_data.get("facets"):
            for facet in facet_data["facets"]:
                if facet.get("field") == "country":
                    regions = [item.get("name") for item in facet.get("counts", []) if item.get("name")]

        # Fallback: use first 20 occurrences to extract unique countries
        if not regions:
            fallback_response = requests.get(f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&limit=20")
            fallback_response.raise_for_status()
            fallback_data = fallback_response.json()
            regions = list({
                record.get("country")
                for record in fallback_data.get("results", [])
                if record.get("country")
            })

        # Step 4: Get synonyms
        syn_response = requests.get(f"https://api.gbif.org/v1/species/{usage_key}/synonyms")
        syn_response.raise_for_status()
        synonyms_data = syn_response.json()
        synonyms = [
            syn.get("scientificName")
            for syn in synonyms_data.get("results", [])
            if syn.get("scientificName")
        ]

        # Step 5: Get habitat info (optional)
        habitats = species_data.get("habitats", [])
        if not habitats:
            habitats = ["Not available"]

        return {
            "taxonomy": taxonomy,
            "regions": regions,
            "synonyms": synonyms,
            "habitats": habitats
        }

    except Exception as e:
        return {
            "taxonomy": "Error fetching taxonomy",
            "regions": [],
            "synonyms": [],
            "habitats": [],
            "error": str(e)
        }
