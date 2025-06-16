import streamlit as st
from services.api_huggingface import classify_image
from services.api_gbif import get_species_info
from services.db_handler import fetch_from_cache, insert_into_cache

st.title("Species Identification App")
st.write("Upload an image or enter a species name to get information!")

# For now, just basic input placeholders
image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
species_name = st.text_input("Or enter species name")

# Inside your button click:
if st.button("Search"):
    category = None

    if image:
        image_bytes = image.read()
        try:
            labels = classify_image(image_bytes)
            
            if not labels:
                st.warning("No labels detected in the image.")
                st.stop()

            st.write("Hugging Face model labels:")
            for label in labels:
                st.write(f"{label['label']} (score: {label['score']:.2f})")

            # Use top label as species_name
            species_name = labels[0]['label']
            st.success(f"Top label selected: {species_name}")

        except Exception as e:
            st.error(f"Error during image analysis: {e}")
            st.stop()

    elif species_name:
        st.info(f"Using entered species name: {species_name}")
    else:
        st.warning("Please upload an image or enter a species name.")
        st.stop()

    # Proceed with cache and GBIF lookup here
    st.write(f"Fetching information for: *{species_name}*")