import streamlit as st
from services.api_inaturalist import identify_species
from services.api_gbif import get_species_info
from services.db_handler import fetch_from_cache, insert_into_cache

st.title("Species Identification App")
st.write("Upload an image or enter a species name to get information!")

# For now, just basic input placeholders
image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
species_name = st.text_input("Or enter species name")

# Inside your button click:
if st.button("Search"):
    if image:
        # Save image temp, or pass mock path
        result = identify_species("mock_image_path.jpg")
        species_name = result["scientific_name"]
        category = result["category"]
    elif species_name:
        species_name = species_name
        category = None
    else:
        st.warning("Please upload an image or enter a species name.")
        st.stop()

    cached = fetch_from_cache(species_name)
    if cached:
        st.success(f"Found in cache: {cached}")
    else:
        st.info("Fetching from GBIF (mock)...")
        gbif_info = get_species_info(species_name)
        insert_into_cache({
            "scientific_name": species_name,
            "common_name": species_name,  # Mock for now
            "category": category,
            "taxonomy": gbif_info["taxonomy"],
            "region": gbif_info["region"],
            "extra_info": {}
        })
        st.write(gbif_info)
