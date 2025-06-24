import streamlit as st
from services.api_huggingface import classify_bird, classify_general
from services.api_plantnet import identify_plant
from services.api_gbif import get_species_info
from services.api_inaturalist import get_scientific_name_from_common, get_common_name
from services.db_handler import fetch_from_cache, insert_into_cache
from services.local_classifier import predict_category
from services.api_wikipedia import get_wikipedia_info

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
            confidence = category_result["confidence"]

            st.success(f"Predicted category: **{category}** (confidence: {confidence:.2f})")

            # Option 1: Warn if confidence is low
            if confidence < 0.65:
                st.warning("⚠️ The model's confidence is low. Please interpret results with caution.")

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
                top_label = labels[0]['label'].split(",")[-1].strip()
                top_score = labels[0]['score']

                if top_score < 0.65:
                    st.warning("⚠️ The top label confidence is low. Please verify the result carefully.")

                species_name = top_label
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

    st.write(f"Fetching information for: *{species_name}*")

    # Step 3: Check cache → GBIF
    cached = fetch_from_cache(species_name)

    if cached:
        st.success("Found in cache:")
        
        # Taxonomy
        st.subheader("Taxonomy")
        taxonomy = cached.get("taxonomy", {})
        if taxonomy:
            st.markdown("\n".join([f"- **{k.capitalize()}**: {v}" for k, v in taxonomy.items()]))
        else:
            st.write("Not available")
        
        # Regions
        st.subheader("Regions")
        regions = cached.get("regions", [])
        if regions:
            st.markdown("\n".join([f"- {r}" for r in regions]))
        else:
            st.write("Not available")

        # Synonyms
        st.subheader("Synonyms")
        synonyms = cached.get("synonyms", [])
        if synonyms:
            st.markdown("\n".join([f"- {s}" for s in synonyms]))
        else:
            st.write("None found")

        # Habitats
        st.subheader("Habitats")
        habitats = cached.get("habitats", [])
        if habitats:
            st.markdown("\n".join([f"- {h}" for h in habitats]))
        else:
            st.write("Not available")

        # Wikipedia Info
        wiki_info = cached.get("wikipedia", {})
        if wiki_info and wiki_info.get("summary"):
            st.subheader("Wikipedia Description")
            st.markdown(wiki_info["summary"])

            if wiki_info.get("image"):
                st.image(wiki_info["image"], caption="Image from Wikipedia", width=400)

            if wiki_info.get("sections"):
                st.subheader("More Info (from Wikipedia)")
                for heading, contents in wiki_info["sections"].items():
                    with st.expander(heading):
                        st.markdown(contents)
            else:
                st.info("No additional sections found.")

            if wiki_info.get("url"):
                st.markdown(f"[Read more on Wikipedia ↗]({wiki_info['url']})")
        else:
            st.write("Wikipedia information not available.")
        
        st.caption(f"📦 Cached on: {cached.get('cached_at')}")


    else:
        st.info("Fetching from GBIF...")
        gbif_info = get_species_info(species_name)
        wiki_info = get_wikipedia_info(species_name)

        insert_into_cache({
            "common_name": common_name,
            "scientific_name": species_name,
            "category": category,
            "taxonomy": gbif_info.get("taxonomy"),
            "regions": gbif_info.get("regions", []),
            "synonyms": gbif_info.get("synonyms", []),
            "extra_info": {},
            "wikipedia": wiki_info
        })

        # Display info nicely
        # Display Taxonomy
        st.subheader("Taxonomy")
        taxonomy = gbif_info.get("taxonomy", {})
        if taxonomy and taxonomy != "Unknown":
            st.json(taxonomy)
        else:
            st.write("Not available")

        # Display Regions
        st.subheader("Regions")
        regions = gbif_info.get("regions", [])
        if regions:
            st.markdown("\n".join([f"- {region}" for region in regions]))
        else:
            st.write("Not available")

        # Display Synonyms
        st.subheader("Synonyms")
        synonyms = gbif_info.get("synonyms", [])
        if synonyms:
            st.markdown("\n".join([f"- {name}" for name in synonyms]))
        else:
            st.write("None found")

        # Step 4: Wikipedia Info
        st.subheader("Wikipedia Description")

        if wiki_info["summary"] != "Not available":
            st.write(wiki_info["summary"])

            if wiki_info.get("image"):
                st.image(wiki_info["image"], caption="Image from Wikipedia", width=400)

            if wiki_info.get("sections"):
                st.subheader("More Info (from Wikipedia)")
                for heading, contents in wiki_info["sections"].items():
                    with st.expander(heading):
                        st.markdown(contents)
            else:
                st.info("No additional sections found.")

            if wiki_info["url"]:
                st.markdown(f"[Read more on Wikipedia ↗]({wiki_info['url']})")
        else:
            st.write("Wikipedia information not available.")