import streamlit as st
import json
import sqlite3
from PIL import Image
import io

from services.api_huggingface import classify_bird, classify_general
from services.api_plantnet import identify_plant
from services.api_gbif import get_species_info
from services.api_inaturalist import get_scientific_name_from_common, get_common_name
from services.db_handler import fetch_from_cache, insert_into_cache, init_db
from services.local_classifier import predict_category
from services.api_wikipedia import get_wikipedia_info
from services.explainability import generate_gradcam

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="FaunaFlora AI — Species Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic Dark-Forest CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:ital,wght@0,400;0,500;1,400&family=Outfit:wght@500;600;700;800&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 30%, #6ee7b7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 0.35rem;
    }

    /* Glass Card Containers */
    .glass-box {
        background: rgba(16, 26, 20, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(12px);
    }

    /* Badges & Tags */
    .custom-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .cache-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border-color: rgba(56, 189, 248, 0.3);
    }

    /* Taxonomy Grid */
    .tax-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.6rem;
        margin-top: 0.75rem;
    }
    .tax-pill {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
    }
    .tax-rank {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        font-weight: 700;
    }
    .tax-val {
        font-size: 0.9rem;
        font-weight: 600;
        color: #f1f5f9;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Scientific Name */
    .sci-name {
        font-family: 'JetBrains Mono', monospace;
        font-style: italic;
        color: #34d399;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    /* Region Pills */
    .region-pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Curated Sample Species for 1-Click Testing
SAMPLE_ITEMS = [
    {"name": "Bengal Tiger", "query": "Panthera tigris tigris", "cat": "Mammal", "desc": "Apex predator of the Indian subcontinent"},
    {"name": "Peregrine Falcon", "query": "Falco peregrinus", "cat": "Bird", "desc": "Fastest animal on Earth (320+ km/h)"},
    {"name": "Monarch Butterfly", "query": "Danaus plexippus", "cat": "Insect", "desc": "Transcontinental migratory marvel"},
    {"name": "Swiss Cheese Plant", "query": "Monstera deliciosa", "cat": "Plant", "desc": "Tropical rainforest fenestrated liana"},
    {"name": "Clownfish", "query": "Amphiprion ocellaris", "cat": "Fish", "desc": "Anemone symbiont of the coral reef"}
]

# Initialize Session State
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "active_category_override" not in st.session_state:
    st.session_state.active_category_override = "Auto-Detect (PyTorch Classifier)"

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### 🌿 FaunaFlora Intelligence")
    st.markdown("**Dual ML + Full-Stack Architecture**")
    st.caption("Multi-stage biological classification with GBIF taxonomy, Wikipedia context, and SQLite cache.")
    
    st.markdown("---")
    st.markdown("#### ⚡ Quick Specimen Showcase")
    for sample in SAMPLE_ITEMS:
        if st.button(f"{sample['name']} ({sample['cat']})", key=f"btn_{sample['name']}", use_container_width=True):
            st.session_state.search_query = sample['query']
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📦 SQLite Cache Queries")
    try:
        conn = sqlite3.connect("db/species_cache.db")
        c = conn.cursor()
        c.execute("SELECT scientific_name, common_name, cached_at FROM species_cache ORDER BY id DESC LIMIT 5")
        cached_history = c.fetchall()
        conn.close()

        if cached_history:
            for item in cached_history:
                name_display = item[1] or item[0]
                if st.button(f"🔍 {name_display}", key=f"hist_{item[0]}", use_container_width=True):
                    st.session_state.search_query = item[0]
                    st.rerun()
        else:
            st.caption("No queries cached yet.")
    except Exception:
        st.caption("Cache database ready.")

    st.markdown("---")
    st.info("💡 **Tip:** You can also run the modern React frontend at `http://localhost:5173` or view REST API docs at `http://localhost:8000/docs`.")

# ----------------- HERO HEADER -----------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Species Intelligence & Identification</div>
    <div class="hero-sub">Multi-stage AI pipeline combining PyTorch category triage, Vision Transformers, Pl@ntNet API, GBIF biodiversity backbone, and Wikipedia enrichment.</div>
</div>
""", unsafe_allow_html=True)

# ----------------- TWO COLUMN WORKSPACE -----------------
col_input, col_output = st.columns([1, 1.35], gap="large")

with col_input:
    st.markdown("### 📷 Specimen Input")
    
    # Input tabs: File upload or Direct Search
    uploaded_image = st.file_uploader("Upload Specimen Image", type=["jpg", "jpeg", "png"], help="Upload a photo of any bird, plant, animal, insect, fish, or reptile.")
    
    # Category Routing Override
    category_options = ["Auto-Detect (PyTorch Classifier)", "Bird", "Plant", "Mammal", "Insect", "Fish", "Reptile_Amphibian"]
    category_override = st.selectbox(
        "Category Routing Pipeline",
        options=category_options,
        index=0,
        help="Leave on Auto-Detect to use the PyTorch EfficientNet router, or select a category manually to force a specific specialist model."
    )

    st.markdown("---")
    st.markdown("##### Or Search By Species Name")
    text_query = st.text_input(
        "Taxonomy Query",
        value=st.session_state.search_query,
        placeholder="e.g. Panthera leo, Bald Eagle, Monstera...",
        help="Enter any scientific or common name to query GBIF and Wikipedia."
    )

    search_clicked = st.button("🚀 Identify & Enrich Specimen", type="primary", use_container_width=True)

    # Show uploaded image preview
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Specimen", use_container_width=True)

# ----------------- EXECUTION PIPELINE -----------------
with col_output:
    if search_clicked or (st.session_state.search_query and not uploaded_image):
        category = None
        category_confidence = None
        top_score = None
        is_low_confidence = False
        warning_msg = None
        model_scores = []
        all_category_scores = []
        cam_data = None
        target_species_name = ""

        # Case 1: Image Uploaded
        if uploaded_image:
            image_bytes = uploaded_image.read()

            with st.status("🔬 Executing Multi-Stage Identification...", expanded=True) as status:
                try:
                    # Stage 1: Broad Category Classification
                    st.write("1️⃣ Running PyTorch Broad Category Classifier...")
                    cat_result = predict_category(image_bytes)
                    predicted_cat = cat_result["category"]
                    predicted_conf = float(cat_result["confidence"])
                    all_category_scores = cat_result.get("all_scores", [])

                    if category_override != "Auto-Detect (PyTorch Classifier)":
                        category = category_override
                        category_confidence = 1.0
                        st.write(f"✓ Using user-selected category override: **{category}**")
                    else:
                        category = predicted_cat
                        category_confidence = predicted_conf
                        st.write(f"✓ Predicted Category: **{category}** (Confidence: {predicted_conf*100:.1f}%)")

                        if predicted_conf < 0.65:
                            is_low_confidence = True
                            warning_msg = f"Broad category classifier confidence is low ({predicted_conf*100:.1f}% for {category}). You can manually override the category on the left if incorrect."

                    # Stage 2: Specialist Model Routing
                    if category == "Bird":
                        st.write("2️⃣ Querying HuggingFace Bird Specialist ViT...")
                        labels = classify_bird(image_bytes)
                        model_scores = labels[:5]
                        top_label = labels[0]["label"].split(",")[-1].strip()
                        top_score = float(labels[0]["score"])
                        target_species_name = top_label

                    elif category == "Plant":
                        st.write("2️⃣ Querying Pl@ntNet Botanical API...")
                        plant_res = identify_plant(image_bytes)
                        target_species_name = plant_res["results"][0]["species"]["scientificNameWithoutAuthor"]
                        top_score = float(plant_res["results"][0].get("score", 0.9))
                        model_scores = [{"label": target_species_name, "score": top_score}]

                    else:
                        st.write(f"2️⃣ Querying General Vision Transformer for {category}...")
                        labels = classify_general(image_bytes)
                        model_scores = labels[:5]
                        top_label = labels[0]["label"].split(",")[-1].strip()
                        top_score = float(labels[0]["score"])
                        target_species_name = top_label

                    if top_score is not None and top_score < 0.65:
                        is_low_confidence = True
                        warning_msg = (warning_msg or "") + f" | Top candidate confidence is low ({top_score*100:.1f}%). Please verify results carefully."

                    # Stage 3: Name Mapping via iNaturalist
                    st.write("3️⃣ Resolving scientific & common names with iNaturalist...")
                    if category != "Plant":
                        mapped = get_scientific_name_from_common(target_species_name)
                        if mapped and mapped.lower() != target_species_name.lower():
                            target_species_name = mapped

                    common_name = get_common_name(target_species_name) or target_species_name

                    # Stage 4: Biodiversity & Encyclopedia Enrichment
                    st.write("4️⃣ Ingesting GBIF taxonomy and Wikipedia encyclopedia...")

                    # Stage 5: Visual Explainability
                    st.write("5️⃣ Computing Grad-CAM visual attention heatmap...")
                    try:
                        cam_data = generate_gradcam(image_bytes, target_category=category)
                    except Exception as ce:
                        print(f"[GRAD-CAM STREAMLIT ERROR] {ce}")

                    status.update(label="✅ Pipeline execution complete!", state="complete", expanded=False)

                except Exception as e:
                    status.update(label=f"❌ Error: {str(e)}", state="error")
                    st.error(f"Inference error: {e}")
                    st.stop()

        # Case 2: Text Query Entered
        elif text_query.strip():
            clean_query = text_query.strip()
            with st.spinner(f"Resolving taxonomy for: {clean_query}..."):
                mapped = get_scientific_name_from_common(clean_query)
                target_species_name = mapped if mapped else clean_query
                common_name = get_common_name(target_species_name) or clean_query
                category = None
                category_confidence = 1.0
                top_score = 1.0

        else:
            st.info("👈 Please upload an image or enter a species name to begin analysis.")
            st.stop()

        # Reset query state after execution
        st.session_state.search_query = ""

        # Step 3: Cache Lookup & Enrichment
        cached = fetch_from_cache(target_species_name)
        if cached:
            species_data = cached
            is_cached = True
        else:
            gbif_info = get_species_info(target_species_name)
            wiki_info = get_wikipedia_info(target_species_name)

            payload = {
                "common_name": common_name,
                "scientific_name": target_species_name,
                "category": category,
                "taxonomy": gbif_info.get("taxonomy") if gbif_info.get("taxonomy") != "Unknown" else {},
                "regions": gbif_info.get("regions", []),
                "coordinates": gbif_info.get("coordinates", []),
                "synonyms": gbif_info.get("synonyms", []),
                "habitats": [],
                "extra_info": {},
                "wikipedia": wiki_info,
                "iucn_status": gbif_info.get("iucn_status")
            }
            insert_into_cache(payload)
            species_data = payload
            is_cached = False

        # ----------------- DISPLAY SPECIES DOSSIER -----------------
        st.markdown("### 📋 Biological Specimen Dossier")

        # Advisory Alert
        if is_low_confidence and warning_msg:
            st.warning(f"⚠️ **Inference Advisory:** {warning_msg}")

        # Hero Header Card
        wiki_image = species_data.get("wikipedia", {}).get("image")
        iucn = species_data.get("iucn_status")
        
        col_img, col_info = st.columns([1, 1.5], gap="medium")
        with col_img:
            if wiki_image:
                st.image(wiki_image, caption=f"{species_data.get('common_name')}", use_container_width=True)
            else:
                st.markdown("🌿 *No representative photo available*")
        
        with col_info:
            st.markdown(f"<h2 style='margin:0; font-size:1.8rem;'>{species_data.get('common_name', target_species_name)}</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='sci-name'>{species_data.get('scientific_name', target_species_name)}</div>", unsafe_allow_html=True)
            
            # Badges
            badge_html = ""
            if category or species_data.get("category"):
                badge_html += f"<span class='custom-badge'>🏷️ {category or species_data.get('category')}</span>"
            if category_confidence:
                badge_html += f"<span class='custom-badge'>🎯 Conf: {int(category_confidence*100)}%</span>"
            if iucn and iucn.get("code"):
                iucn_code = iucn.get("code")
                badge_html += f"<span class='custom-badge' style='background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3);'>🛡️ IUCN: {iucn_code}</span>"
            if is_cached:
                badge_html += f"<span class='custom-badge cache-badge'>⚡ SQLite Cached</span>"
            else:
                badge_html += f"<span class='custom-badge'>🌐 Live Enriched</span>"
            st.markdown(badge_html, unsafe_allow_html=True)

            if is_cached and species_data.get("cached_at"):
                st.caption(f"Cached on: {species_data.get('cached_at')}")

        # IUCN Conservation Banner
        if iucn and (iucn.get("code") or iucn.get("category")):
            code = iucn.get("code", "")
            cat_name = iucn.get("category", "")
            url = iucn.get("iucn_url")
            color = "#ef4444" if code in ["CR", "EN"] else ("#f59e0b" if code in ["VU", "NT"] else "#10b981")
            url_link = f" — <a href='{url}' target='_blank' style='color: #38bdf8;'>View IUCN Dossier ↗</a>" if url else ""
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); border-left: 4px solid {color}; padding: 0.75rem 1rem; border-radius: 8px; margin: 1rem 0;">
                <div style="font-weight: 700; color: {color}; font-size: 0.95rem;">
                    🛡️ IUCN Red List: {cat_name} ({code})
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">
                    Official Global Biodiversity Threat Assessment{url_link}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Top Model Predictions Bar
        if model_scores:
            st.markdown("#### 🎯 Prediction Candidate Scores")
            for item in model_scores[:5]:
                score_pct = float(item["score"])
                st.write(f"**{item['label']}** ({score_pct*100:.1f}%)")
                st.progress(score_pct)

        # PyTorch Broad Category Probabilities
        if all_category_scores:
            with st.expander("📊 Broad Category Probability Breakdown (PyTorch Router)"):
                for s in all_category_scores:
                    conf = float(s["confidence"])
                    st.write(f"**{s['category'].replace('_', ' / ')}**: {conf*100:.1f}%")
                    st.progress(conf)

        # AI Visual Explainability (Grad-CAM)
        if cam_data:
            with st.expander("🧠 AI Visual Explainability (Grad-CAM Attention Heatmap)", expanded=True):
                st.caption(cam_data["description"])
                col_cam1, col_cam2 = st.columns(2)
                with col_cam1:
                    st.image(cam_data["overlay_image"], caption="Grad-CAM Activation Overlay (ConvHead Layer)", use_container_width=True)
                with col_cam2:
                    st.image(cam_data["heatmap_image"], caption="Raw Attention Heatmap Mask", use_container_width=True)
                st.info("💡 **How to interpret:** Warm red/yellow zones indicate the most discriminative biological features (e.g. beak, wing markings, petal structure) identified by the convolutional neural network.")


        # Taxonomy Cards (GBIF)
        taxonomy = species_data.get("taxonomy", {})
        if taxonomy and isinstance(taxonomy, dict) and any(taxonomy.values()):
            st.markdown("#### 🧬 Biological Taxonomy (GBIF)")
            tax_order = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]
            pills = []
            for rank in tax_order:
                val = taxonomy.get(rank)
                if val:
                    pills.append(f"<div class='tax-pill'><div class='tax-rank'>{rank}</div><div class='tax-val'>{val}</div></div>")
            if pills:
                st.markdown(f"<div class='tax-grid'>{''.join(pills)}</div>", unsafe_allow_html=True)

        # Wikipedia Encyclopedic Knowledge
        wiki = species_data.get("wikipedia", {})
        if wiki:
            st.markdown("#### 📖 Species Description & Encyclopedia")
            summary = wiki.get("summary")
            if summary and summary != "Not available":
                st.write(summary)

            # Structured Sections Accordions
            sections = wiki.get("sections", {})
            if sections:
                for heading, content in sections.items():
                    with st.expander(f"📌 {heading}"):
                        st.markdown(content)

            if wiki.get("url"):
                st.markdown(f"[Read complete article on Wikipedia ↗]({wiki['url']})")

        # Global Specimen Sightings Map (GBIF Coordinates)
        coordinates = species_data.get("coordinates", [])
        if coordinates:
            st.markdown("#### 🌍 Global Specimen Sightings Map (GBIF)")
            import pandas as pd
            df_coords = pd.DataFrame([
                {"latitude": pt["lat"], "longitude": pt["lng"]}
                for pt in coordinates if "lat" in pt and "lng" in pt
            ])
            if not df_coords.empty:
                st.map(df_coords, zoom=1)
                st.caption(f"📍 Plotted {len(df_coords)} georeferenced observation records from GBIF occurrences.")

        # Occurrence Regions & Synonyms
        regions = species_data.get("regions", [])
        synonyms = species_data.get("synonyms", [])
        
        col_reg, col_syn = st.columns(2)
        with col_reg:
            if regions:
                st.markdown("#### 🌍 Recorded Occurrence Regions")
                pills = [f"<span class='region-pill'>📍 {r}</span>" for r in regions]
                st.markdown("".join(pills), unsafe_allow_html=True)
        with col_syn:
            if synonyms:
                st.markdown("#### 🏷️ Scientific Synonyms")
                for syn in synonyms[:6]:
                    st.caption(f"• *{syn}*")

    else:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 2rem; background: rgba(16, 26, 20, 0.4); border: 1px dashed rgba(16, 185, 129, 0.25); border-radius: 16px;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🌿</div>
            <h3 style="color: #ffffff; margin-bottom: 0.5rem;">Ready for Specimen Analysis</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; max-width: 450px; margin: 0 auto;">
                Upload an image on the left or select any sample from the sidebar to execute the multi-stage identification pipeline.
            </p>
        </div>
        """, unsafe_allow_html=True)