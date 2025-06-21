import streamlit as st
from services.api_huggingface import classify_bird, classify_general
from services.api_plantnet import identify_plant
from services.api_gbif import get_species_info
from services.api_inaturalist import get_scientific_name_from_common, get_common_name
from services.db_handler import fetch_from_cache, insert_into_cache
from services.local_classifier import predict_category

st.title("Species Identification App")
st.write("Upload an image or enter a species name to get information!")

image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
species_name = st.text_input("Or enter species name")

if st.button("Search"):
    category = None

    if image:
        image_bytes = image.read()

        try:
            # Step 1: Predict category
            with st.spinner("Identifying species..."):
                category_result = predict_category(image_bytes)

            category = category_result["category"]
            st.success(f"Predicted category: **{category}** (confidence: {category_result['confidence']:.2f})")

            # Step 2: Route to appropriate classifier
            if category == "Bird":
                st.info("Using bird species classifier...")
                labels = classify_bird(image_bytes)

            elif category == "Plant":
                st.info("Using Pl@ntNet for plant identification...")
                result = identify_plant(image_bytes)
                try:
                    species_name = result["results"][0]["species"]["scientificNameWithoutAuthor"]
                    st.success(f"Plant identified: {species_name}")
                except:
                    st.warning("Could not extract plant name.")
                    st.stop()

            else:
                st.info("Using general classifier for other categories...")
                labels = classify_general(image_bytes)

            # Parse labels (for HF-based classifiers)
            if category != "Plant":
                if not labels:
                    st.warning("No labels detected.")
                    st.stop()

                st.write("Model labels:")
                for label in labels:
                    st.write(f"{label['label']} (score: {label['score']:.2f})")

                # Extract last part after comma (likely scientific name or clean label)
                species_name = labels[0]['label'].split(",")[-1].strip()
                st.success(f"Top label selected: {species_name}")

        except Exception as e:
            st.error(f"Error during image analysis: {e}")
            st.stop()

    elif species_name:
        st.info(f"Using entered species name: {species_name}")
    else:
        st.warning("Please upload an image or enter a species name.")
        st.stop()

    species_name = species_name.strip()

    # For non-plant: Map to scientific name using iNaturalist if needed
    if category != "Plant":
        mapped_name = get_scientific_name_from_common(species_name)
        if mapped_name and mapped_name.lower() != species_name.lower():
            st.info(f"Mapped to scientific name: {mapped_name}")
            species_name = mapped_name
    common_name = get_common_name(species_name) or species_name


    # Step 3: Check cache → GBIF
    st.write(f"Fetching information for: *{species_name}*")
    cached = fetch_from_cache(species_name)
    if cached:
        st.success(f"Found in cache: {cached}")
    else:
        st.info("Fetching from GBIF...")
        gbif_info = get_species_info(species_name)
        insert_into_cache({
            "common_name": common_name,
            "scientific_name": species_name,
            "category": category,
            "taxonomy": gbif_info.get("taxonomy"),
            "region": gbif_info.get("region"),
            "extra_info": {}
        })
        st.write(gbif_info)
