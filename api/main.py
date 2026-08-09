import os
import io
import json
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services.api_huggingface import classify_bird, classify_general
from services.api_plantnet import identify_plant
from services.api_gbif import get_species_info
from services.api_inaturalist import get_scientific_name_from_common, get_common_name
from services.db_handler import fetch_from_cache, insert_into_cache, init_db
from services.local_classifier import predict_category
from services.api_wikipedia import get_wikipedia_info
from services.explainability import generate_gradcam
from services.report_generator import generate_markdown_dossier
from api.schemas import (
    SpeciesDetailResponse,
    WikipediaInfo,
    ExplainabilityInfo,
    IUCNStatus,
    ModelScore,
    SampleSpeciesItem,
    HistoryItem,
    HealthResponse
)

# Curated sample species for 1-click portfolio demonstration
CURATED_SAMPLES = [
    SampleSpeciesItem(
        name="Bengal Tiger",
        scientific_name="Panthera tigris tigris",
        category="Mammal",
        tag="Apex Predator",
        description="The Bengal tiger is the most numerous tiger subspecies, native to the Indian subcontinent.",
        sample_image="https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=600&q=80"
    ),
    SampleSpeciesItem(
        name="Peregrine Falcon",
        scientific_name="Falco peregrinus",
        category="Bird",
        tag="Fastest Animal",
        description="Renowned for its speed, reaching over 320 km/h (200 mph) during its characteristic hunting dive.",
        sample_image="https://images.unsplash.com/photo-1611689342806-0863700ce1e4?auto=format&fit=crop&w=600&q=80"
    ),
    SampleSpeciesItem(
        name="Monarch Butterfly",
        scientific_name="Danaus plexippus",
        category="Insect",
        tag="Migratory Wonder",
        description="Famous for its incredible seasonal migration across North America spanning thousands of kilometers.",
        sample_image="https://images.unsplash.com/photo-1549480017-d76466a4b7e8?auto=format&fit=crop&w=600&q=80"
    ),
    SampleSpeciesItem(
        name="Swiss Cheese Plant",
        scientific_name="Monstera deliciosa",
        category="Plant",
        tag="Tropical Flora",
        description="An iconic tropical liana native to the rainforests of Central America, famed for its perforated fenestrated leaves.",
        sample_image="https://images.unsplash.com/photo-1614594975525-e45190c55d0b?auto=format&fit=crop&w=600&q=80"
    ),
    SampleSpeciesItem(
        name="Ocellaris Clownfish",
        scientific_name="Amphiprion ocellaris",
        category="Fish",
        tag="Marine Symbiosis",
        description="A bright orange marine fish living in mutualistic symbiosis with stinging sea anemones.",
        sample_image="https://images.unsplash.com/photo-1535591273668-578e31182c4f?auto=format&fit=crop&w=600&q=80"
    ),
    SampleSpeciesItem(
        name="Green Iguana",
        scientific_name="Iguana iguana",
        category="Reptile_Amphibian",
        tag="Arboreal Herbivore",
        description="A large, arboreal herbivorous lizard native to Central and South America and the Caribbean.",
        sample_image="https://images.unsplash.com/photo-1582845512747-e42001c95638?auto=format&fit=crop&w=600&q=80"
    )
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    os.makedirs("db", exist_ok=True)
    init_db()
    print("[INFO] Species Identification API initialized successfully.")
    yield
    print("[INFO] Shutting down Species Identification API.")

app = FastAPI(
    title="Species Identification & Biodiversity Intelligence API",
    description="Full-stack multi-model AI system for hierarchical species identification, taxonomy resolution, and ecological enrichment.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend clients (Vite dev and production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_or_enrich_species(scientific_name: str, common_name: Optional[str] = None, category: Optional[str] = None) -> dict:
    """Helper to check cache or query GBIF + Wikipedia and cache the result."""
    clean_scientific = scientific_name.strip()
    cached = fetch_from_cache(clean_scientific)

    if cached:
        return {**cached, "cached": True, "source": "cache"}

    # Live lookup
    gbif_info = get_species_info(clean_scientific)
    wiki_info = get_wikipedia_info(clean_scientific)

    resolved_common = common_name or get_common_name(clean_scientific) or clean_scientific

    cache_payload = {
        "common_name": resolved_common,
        "scientific_name": clean_scientific,
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

    try:
        insert_into_cache(cache_payload)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to insert into cache: {e}")

    return {**cache_payload, "cached": False, "source": "live", "cached_at": None}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint validating API and database connectivity."""
    db_ok = os.path.exists("db/species_cache.db")
    return HealthResponse(
        status="healthy",
        models_ready=True,
        db_connected=db_ok,
        version="1.0.0"
    )


@app.get("/api/samples", response_model=List[SampleSpeciesItem])
async def get_samples():
    """Get curated sample species for instant UI exploration."""
    return CURATED_SAMPLES


@app.get("/api/history", response_model=List[HistoryItem])
async def get_history(limit: int = Query(12, ge=1, le=50)):
    """Fetch recently cached species queries from SQLite."""
    history = []
    try:
        conn = sqlite3.connect("db/species_cache.db")
        c = conn.cursor()
        c.execute("""
            SELECT scientific_name, common_name, category, cached_at, wikipedia_json 
            FROM species_cache 
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()

        for row in rows:
            thumbnail = None
            if row[4]:
                try:
                    wiki_data = json.loads(row[4])
                    thumbnail = wiki_data.get("image")
                except:
                    pass

            history.append(HistoryItem(
                scientific_name=row[0],
                common_name=row[1],
                category=row[2],
                cached_at=row[3],
                thumbnail=thumbnail
            ))
    except Exception as e:
        print(f"[HISTORY ERROR] {e}")

    return history


@app.get("/api/species/{species_name}", response_model=SpeciesDetailResponse)
async def get_species_by_name(species_name: str):
    """Direct query endpoint for species details by common or scientific name."""
    clean_name = species_name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Species name cannot be empty.")

    # Try mapping to scientific name via iNaturalist if not already scientific
    scientific_name = get_scientific_name_from_common(clean_name) or clean_name
    common_name = get_common_name(scientific_name) or clean_name

    data = fetch_or_enrich_species(scientific_name=scientific_name, common_name=common_name)

    wiki_data = data.get("wikipedia", {})
    wikipedia_obj = WikipediaInfo(
        summary=wiki_data.get("summary", "Not available"),
        image=wiki_data.get("image"),
        url=wiki_data.get("url"),
        sections=wiki_data.get("sections", {})
    )

    return SpeciesDetailResponse(
        common_name=data.get("common_name", common_name),
        scientific_name=data.get("scientific_name", scientific_name),
        category=data.get("category"),
        confidence=1.0,
        category_confidence=1.0,
        is_low_confidence=False,
        warning_message=None,
        model_scores=[],
        taxonomy=data.get("taxonomy") if isinstance(data.get("taxonomy"), dict) else {},
        regions=data.get("regions", []),
        coordinates=data.get("coordinates", []),
        synonyms=data.get("synonyms", []),
        habitats=data.get("habitats", []),
        iucn_status=data.get("iucn_status"),
        wikipedia=wikipedia_obj,
        cached=data.get("cached", False),
        cached_at=data.get("cached_at"),
        source=data.get("source", "live")
    )


@app.get("/api/species/{name}/export", response_class=PlainTextResponse)
async def export_species_report(name: str):
    """
    Exports a comprehensive biological field dossier in formatted Markdown.
    """
    clean_name = name.strip()
    data = fetch_or_enrich_species(scientific_name=clean_name)
    md_report = generate_markdown_dossier(data)
    safe_filename = clean_name.replace(" ", "_").lower()
    return PlainTextResponse(
        content=md_report,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}_field_dossier.md"'}
    )


@app.post("/api/identify", response_model=SpeciesDetailResponse)
async def identify_species(
    image: Optional[UploadFile] = File(None),
    species_name: Optional[str] = Form(None),
    category_override: Optional[str] = Form(None)
):
    """
    Main identification pipeline endpoint:
    1. Runs PyTorch Broad Category Classifier on uploaded image (or uses category_override if provided).
    2. Routes to specialized model (HuggingFace Bird ViT, Pl@ntNet API, or General ViT).
    3. Resolves common / scientific names with iNaturalist.
    4. Retrieves structured taxonomy, occurrence regions, synonyms from GBIF.
    5. Retrieves descriptive encyclopedia data from Wikipedia.
    6. Returns unified payload with confidence warnings, category scores, and caching status.
    """
    category = None
    category_confidence = None
    top_score = None
    is_low_confidence = False
    is_category_overridden = False
    warning_messages = []
    all_category_scores = []
    model_scores: List[ModelScore] = []
    target_species_name = None

    # Scenario A: Image upload provided
    if image is not None:
        try:
            image_bytes = await image.read()
            if not image_bytes:
                raise HTTPException(status_code=400, detail="Uploaded image file is empty.")

            # Stage 1: Predict Broad Biological Category
            category_result = predict_category(image_bytes)
            predicted_category = category_result["category"]
            predicted_confidence = float(category_result["confidence"])

            # Map all category scores
            if "all_scores" in category_result:
                all_category_scores = [
                    {"category": s["category"], "confidence": float(s["confidence"])}
                    for s in category_result["all_scores"]
                ]

            # Apply category override if user specified one
            if category_override and category_override.strip() in ['Bird', 'Fish', 'Insect', 'Mammal', 'Plant', 'Reptile_Amphibian']:
                category = category_override.strip()
                category_confidence = 1.0
                is_category_overridden = True
            else:
                category = predicted_category
                category_confidence = predicted_confidence
                if category_confidence < 0.65:
                    is_low_confidence = True
                    warning_messages.append(
                        f"Category classifier confidence is low ({category_confidence*100:.1f}% for {category}). You can manually select the correct category below."
                    )

            # Stage 2: Specialized Model Routing
            if category == "Bird":
                labels = classify_bird(image_bytes)
                for item in labels[:5]:
                    model_scores.append(ModelScore(label=item["label"], score=float(item["score"])))

                top_label = labels[0]["label"].split(",")[-1].strip()
                top_score = float(labels[0]["score"])
                target_species_name = top_label

            elif category == "Plant":
                try:
                    plant_res = identify_plant(image_bytes)
                    target_species_name = plant_res["results"][0]["species"]["scientificNameWithoutAuthor"]
                    top_score = float(plant_res["results"][0].get("score", 0.9))
                    model_scores.append(ModelScore(label=target_species_name, score=top_score))
                except Exception as e:
                    print(f"[PLANT IDENT ERROR] {e}")
                    raise HTTPException(
                        status_code=422,
                        detail=f"Botany identification could not identify the plant sample ({str(e)})."
                    )

            else:
                # General Classifier
                labels = classify_general(image_bytes)
                for item in labels[:5]:
                    model_scores.append(ModelScore(label=item["label"], score=float(item["score"])))

                top_label = labels[0]["label"].split(",")[-1].strip()
                top_score = float(labels[0]["score"])
                target_species_name = top_label

            if top_score is not None and top_score < 0.65:
                is_low_confidence = True
                warning_messages.append(
                    f"Species identification confidence is low ({top_score*100:.1f}%). Please verify with caution."
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image inference error: {str(e)}")

    # Scenario B: Species text input provided
    elif species_name and species_name.strip():
        target_species_name = species_name.strip()
        top_score = 1.0
        category_confidence = 1.0

    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide an image file or a species name."
        )

    # Stage 3: Scientific Name Normalization
    if category != "Plant":
        mapped_name = get_scientific_name_from_common(target_species_name)
        if mapped_name and mapped_name.lower() != target_species_name.lower():
            target_species_name = mapped_name

    common_name = get_common_name(target_species_name) or target_species_name

    # Stage 4 & 5: Cache Lookup & Enrichment (GBIF + Wikipedia)
    data = fetch_or_enrich_species(
        scientific_name=target_species_name,
        common_name=common_name,
        category=category
    )

    wiki_data = data.get("wikipedia", {})
    wikipedia_obj = WikipediaInfo(
        summary=wiki_data.get("summary", "Not available"),
        image=wiki_data.get("image"),
        url=wiki_data.get("url"),
        sections=wiki_data.get("sections", {})
    )

    # Stage 6: Visual Model Explainability (Grad-CAM)
    explainability_data = None
    if image is not None and image_bytes:
        try:
            cam_res = generate_gradcam(image_bytes, target_category=category)
            explainability_data = ExplainabilityInfo(
                overlay_image=cam_res["overlay_image"],
                heatmap_image=cam_res["heatmap_image"],
                target_category=cam_res["target_category"],
                confidence=cam_res["confidence"],
                description=cam_res["description"]
            )
        except Exception as e:
            print(f"[GRAD-CAM EXPLAINABILITY ERROR] {e}")

    warning_text = " | ".join(warning_messages) if warning_messages else None

    return SpeciesDetailResponse(
        common_name=data.get("common_name", common_name),
        scientific_name=data.get("scientific_name", target_species_name),
        category=category or data.get("category"),
        confidence=top_score,
        category_confidence=category_confidence,
        is_low_confidence=is_low_confidence,
        is_category_overridden=is_category_overridden,
        warning_message=warning_text,
        all_category_scores=all_category_scores,
        model_scores=model_scores,
        explainability=explainability_data,
        taxonomy=data.get("taxonomy") if isinstance(data.get("taxonomy"), dict) else {},
        regions=data.get("regions", []),
        coordinates=data.get("coordinates", []),
        synonyms=data.get("synonyms", []),
        habitats=data.get("habitats", []),
        iucn_status=data.get("iucn_status"),
        wikipedia=wikipedia_obj,
        cached=data.get("cached", False),
        cached_at=data.get("cached_at"),
        source=data.get("source", "live")
    )

# Static file serving for production build
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"detail": "Frontend not found"}, status_code=404)

