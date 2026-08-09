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
                "synonyms": []
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

        # Step 4: Get georeferenced observation coordinates for interactive map
        coordinates = []
        try:
            coord_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=40"
            coord_response = requests.get(coord_url, timeout=10)
            if coord_response.status_code == 200:
                for rec in coord_response.json().get("results", []):
                    lat = rec.get("decimalLatitude")
                    lng = rec.get("decimalLongitude")
                    if lat is not None and lng is not None:
                        coordinates.append({
                            "lat": float(lat),
                            "lng": float(lng),
                            "country": rec.get("country", "Unknown"),
                            "year": rec.get("year"),
                            "locality": rec.get("locality") or rec.get("stateProvince") or rec.get("country", "")
                        })
        except Exception as ce:
            print(f"[GBIF COORDINATES ERROR] {ce}")

        # Step 5: Get synonyms
        syn_response = requests.get(f"https://api.gbif.org/v1/species/{usage_key}/synonyms")
        syn_response.raise_for_status()
        synonyms_data = syn_response.json()
        synonyms = [
            syn.get("scientificName")
            for syn in synonyms_data.get("results", [])
            if syn.get("scientificName")
        ]

        # Step 6: Get official IUCN Red List conservation status
        iucn_status = None
        try:
            iucn_url = f"https://api.gbif.org/v1/species/{usage_key}/iucnRedListCategory"
            iucn_resp = requests.get(iucn_url, timeout=8)
            if iucn_resp.status_code == 200:
                iucn_json = iucn_resp.json()
                code = iucn_json.get("code")
                category_name = iucn_json.get("category")
                taxon_id = iucn_json.get("iucnTaxonID")
                if code or category_name:
                    iucn_status = {
                        "code": code,
                        "category": category_name,
                        "iucn_taxon_id": str(taxon_id) if taxon_id else None,
                        "iucn_url": f"https://www.iucnredlist.org/species/{taxon_id}" if taxon_id else None
                    }
        except Exception as ie:
            print(f"[GBIF IUCN ERROR] {ie}")

        return {
            "taxonomy": taxonomy,
            "regions": regions,
            "coordinates": coordinates,
            "synonyms": synonyms,
            "iucn_status": iucn_status
        }

    except Exception as e:
        return {
            "taxonomy": "Error fetching taxonomy",
            "regions": [],
            "coordinates": [],
            "synonyms": [],
            "iucn_status": None,
            "error": str(e)
        }
