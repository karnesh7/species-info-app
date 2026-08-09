# FaunaFlora AI — Species Identification & Biodiversity Intelligence System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite_5-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-19.4-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![SQLite](https://img.shields.io/badge/SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An intelligent, full-stack biodiversity platform that identifies biological species from photographs or text queries. The system combines a **hierarchical multi-stage ML pipeline**, visual explainability (**Grad-CAM**), geospatial observation mapping (**GBIF + Leaflet**), official **IUCN Red List** conservation ratings, and encyclopedic knowledge enrichment.

The application offers both a modern **React + Vite** web interface and an updated standalone **Streamlit** dashboard, powered by an asynchronous **FastAPI** backend.

---

## 🌟 How It Works: Pipeline Architecture

```
                          [Specimen Image / Species Name]
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │  Stage 1: Broad Categorizer   │  <-- PyTorch EfficientNet-B0
                         │ (Bird, Plant, Mammal, Insect, │      Fast coarse triage (~15ms)
                         │   Fish, Reptile/Amphibian)    │
                         └───────────────┬───────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
           ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
           │   Bird ViT       │ │   Pl@ntNet API   │ │   General ViT    │
           │ (HuggingFace)    │ │ (Botany Expert)  │ │ (Vision Transf.) │
           └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
                    │                    │                    │
                    └────────────────────┼────────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │  Stage 3: Taxon Normalization │  <-- iNaturalist API
                         │   (Common ⟷ Scientific Name) │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │    Multi-Tier SQLite Cache    │  <-- <5ms cached response
                         │     (db/species_cache.db)     │
                         └───────┬───────────────┬───────┘
                           HIT   │               │ MISS
                                 │               ▼
                                 │    ┌──────────────────────────┐
                                 │    │ GBIF Taxonomy & Regions  │
                                 │    │ GBIF Sighting Coords     │
                                 │    │ IUCN Red List Status     │
                                 │    │ Wikipedia Encyclopedia   │
                                 │    └──────────┬───────────────┘
                                 │               │
                                 └───────┬───────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │      Biological Dossier       │
                         │  • Taxonomy Hierarchy Tree    │
                         │  • Grad-CAM Visual Heatmap    │
                         │  • Interactive Sighting Map   │
                         │  • IUCN Conservation Status   │
                         │  • Field Dossier (.md / .pdf) │
                         └───────────────────────────────┘
```

---

## 🌿 Core Features

### 1. 🔍 Multi-Stage Species Identification
* **Hierarchical Coarse-to-Fine Routing**: Rather than relying on a single generic model, the system first triages specimens across **6 broad biological categories** using a local PyTorch EfficientNet model, then dispatches the image to domain-specialist models:
  * **Birds**: HuggingFace Vision Transformer (`chriamue/bird-species-classifier`).
  * **Plants & Flora**: Pl@ntNet Botanical Identification API.
  * **Mammals, Insects, Fish, Reptiles & Amphibians**: General Vision Transformer (`google/vit-base-patch16-224`).
* **Manual Category Override**: If a photo is noisy or low-confidence, users can manually select the broad category to route the specimen directly to the appropriate specialist model.
* **Low-Confidence Warning System**: Automatically alerts users when prediction scores fall below confidence thresholds, encouraging careful verification.

### 2. 🧬 Taxonomic Classification & Biological Hierarchy
* **GBIF Backbone Integration**: Ingests complete biological taxonomic trees from Kingdom down to Species:
  $$\text{Kingdom} \longrightarrow \text{Phylum} \longrightarrow \text{Class} \longrightarrow \text{Order} \longrightarrow \text{Family} \longrightarrow \text{Genus} \longrightarrow \text{Species}$$
* **Name Resolution via iNaturalist**: Bidirectionally maps vernacular/common names to valid binomial scientific names (and vice versa).

### 3. 📖 Natural History & Encyclopedic Knowledge
* **Structured Wikipedia Extraction**: Parses encyclopedic summaries and dedicated structured sections for:
  * **Diet & Foraging**: Nutritional behavior and prey preferences.
  * **Habitat & Distribution**: Biomes, geographical range, and ecological niche.
  * **Physical Description**: Size, coloration, morphology, and distinguishing field marks.
  * **Behavior & Social Structure**: Mating, territoriality, and diurnal/nocturnal habits.
* **Scientific Synonyms & Known Aliases**: Lists historical scientific names and taxonomic synonyms.

### 4. 🧠 Visual Model Explainability (Grad-CAM)
* **PyTorch Activation Mapping**: Hooks into `model.conv_head` during backpropagation to generate a gradient-weighted class activation map.
* **Interactive Heatmap Inspector**: Allows users to dynamically slide between the original specimen photo, the blended Turbo colormap, and the raw attention mask, visually verifying that the model focused on authentic biological features (e.g. beak, wing markings, leaf venation) rather than background artifacts.

### 5. 🌍 Interactive Global Sightings Map
* **GBIF Georeferenced Coordinates**: Queries live observation records with latitude, longitude, country, locality, and sighting year.
* **Leaflet Dark-Mode GIS Map**: Renders glowing observation points across the globe with interactive popups detailing individual sightings.

### 6. 🛡️ Live IUCN Red List Conservation Status
* **Global Threat Ratings**: Ingests official IUCN categories (`Extinct`, `Critically Endangered`, `Endangered`, `Vulnerable`, `Near Threatened`, `Least Concern`, `Data Deficient`).
* **Visual Conservation Spectrum**: Displays an interactive 7-tier spectrum meter highlighting the specimen's threat classification with direct links to official IUCN assessment dossiers.

### 7. 📄 Export Specimen Field Dossier (PDF & Markdown)
* **1-Click Markdown Download**: Downloads a formatted `.md` field report containing taxonomy tables, IUCN rating, model confidence scores, occurrence regions, and encyclopedia summaries.
* **Print / Save as PDF**: Print-optimized stylesheet that formats a clean biological field sheet ready for PDF export via `window.print()`.
* **Clipboard Sync**: Instantly copies formatted Markdown notes to the clipboard.

### 8. ⚡ High-Performance Caching & Dual Interfaces
* **Persistent SQLite Caching**: Caches full species dossiers, taxonomy trees, coordinates, and IUCN statuses locally, delivering $<5\text{ms}$ lookups on repeated queries.
* **Modern React + Vite Web App**: Dark-forest glassmorphism UI with live specimen dropzone, device camera capture, and 5-stage animated pipeline stepper.
* **Updated Streamlit Dashboard**: Standalone dashboard with quick specimen showcase buttons and SQLite history explorer.

---

## 🧑‍💻 Technology Stack

| Layer | Technologies | Purpose & Role |
| :--- | :--- | :--- |
| **Frontend UI** | React 18, Vite 5, Leaflet, Lucide Icons | Responsive glassmorphic web interface, interactive GIS mapping, and fast build times. |
| **Backend REST API** | FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous REST endpoints with automated OpenAPI/Swagger specs. |
| **Machine Learning** | PyTorch, Torchvision, HuggingFace Transformers | Local EfficientNet-B0 broad triage model and cloud Vision Transformers. |
| **Explainable AI (XAI)** | PyTorch Hooks + NumPy Turbo Colormap | Native Grad-CAM visual explainability heatmap engine without external dependencies. |
| **Biodiversity APIs** | GBIF Backbone, iNaturalist, IUCN Red List, Wikipedia API | Real-time biological data fusion for taxonomy, coordinates, threat status, and natural history. |
| **Data Storage / Cache** | SQLite3 (JSON-serialized storage) | Local persistence layer for instantaneous $<5\text{ms}$ cached lookups and offline retrieval. |
| **Alternative UI** | Streamlit | Standalone, lightweight data dashboard for quick local execution (`app.py`). |

---

## 📡 REST API Reference

The FastAPI backend exposes the following REST endpoints:

| Method | Endpoint | Description | Parameters / Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/identify` | Multi-stage image/text identification & enrichment | `image` (UploadFile, opt), `species_name` (Form, opt), `category_override` (Form, opt) |
| `GET` | `/api/species/{name}` | Direct taxonomy & encyclopedia lookup (cache-checked) | `name` (Path param: scientific or common name) |
| `GET` | `/api/species/{name}/export` | Download formatted Markdown field dossier | `name` (Path param) $\rightarrow$ returns `.md` file attachment |
| `GET` | `/api/samples` | Curated showcase specimens for 1-click exploration | Returns list with images, categories, and descriptions |
| `GET` | `/api/history` | Recent cached queries from SQLite database | `limit` (Query param, default: 20) |
| `GET` | `/api/health` | Service and database connectivity health check | Returns status and database integrity |

> 📖 **Interactive Swagger Documentation**: Explore and test all endpoints live at `http://localhost:8000/docs`

---

## 🧠 Local Classifier Details

* **Model Architecture**: Fine-tuned **EfficientNet-B0** exported as a standalone PyTorch `.pt` model.
* **Classes (6)**: `Bird`, `Fish`, `Insect`, `Mammal`, `Plant`, `Reptile_Amphibian`.
* **Accuracy & Latency**: **~96%** validation accuracy with sub-20ms CPU inference time.
* **Google Colab Notebook**: 📓 [Train Classifier on Google Colab](https://colab.research.google.com/github/karnesh7/species-info-app/blob/main/notebooks/train_classifier.ipynb)

---

## 🛠️ Installation & Setup

### 1. Prerequisites
* **Python 3.10+** (tested on Python 3.11)
* **Node.js 18+** and **npm**

### 2. Clone & Virtual Environment Setup

```bash
git clone https://github.com/karnesh7/species-info-app.git
cd species-info-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
PLANTNET_API_KEY=your_plantnet_api_key_here
HF_TOKEN=your_huggingface_token_here
```

---

## 🏃 Running the Application

### Option A: Modern Full-Stack Web App (Recommended)

**Terminal 1 — Start the FastAPI Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```
> API available at: `http://localhost:8000` | Swagger Docs: `http://localhost:8000/docs`

**Terminal 2 — Start the React Frontend:**
```bash
cd frontend
npm install
npm run dev
```
> Web interface accessible at: `http://localhost:5173`

---

### Option B: Production Single-Server Bundle

Build the React frontend and serve everything directly from FastAPI on a single port:

```bash
cd frontend
npm run build
cd ..
uvicorn api.main:app --port 8000
```
> Full-Stack application running at: `http://localhost:8000`

---

### Option C: Standalone Streamlit Dashboard

```bash
streamlit run app.py
```
> Streamlit interface running at: `http://localhost:8501`

---

## 📁 Project Structure

```
species-info-app/
├── api/                              # FastAPI Gateway & Data Validation
│   ├── __init__.py
│   ├── main.py                       # REST routes, CORS, static mounting & export
│   └── schemas.py                    # Pydantic v2 validation models
│
├── frontend/                         # Modern React + Vite Frontend
│   ├── index.html                    # HTML entry with Google Fonts & Leaflet CSS
│   ├── vite.config.js                # Vite configuration with /api proxy
│   ├── package.json
│   └── src/
│       ├── App.jsx                   # Central application state & pipeline controller
│       ├── index.css                 # Glassmorphic nature design system
│       └── components/
│           ├── Header.jsx            # Top navbar & Swagger doc link
│           ├── SampleChips.jsx       # 1-click exploration showcase
│           ├── Dropzone.jsx          # Drag-and-drop & device camera input
│           ├── PipelineStatus.jsx    # Real-time 5-stage animated stepper
│           ├── SpeciesDossier.jsx    # Hero species card & status badges
│           ├── ExplainabilityViewer.jsx # Grad-CAM attention heatmap slider
│           ├── InteractiveMap.jsx    # Leaflet dark world sightings map
│           ├── ConservationBadge.jsx # IUCN Red List spectrum meter
│           ├── ExportDossierModal.jsx# Markdown download & PDF print modal
│           ├── TaxonomyTree.jsx      # Visual biological hierarchy tree
│           ├── ConfidenceMeter.jsx   # Candidate prediction score bars
│           ├── WikipediaViewer.jsx   # Encyclopedic accordion sections
│           ├── OccurrenceMap.jsx     # Occurrence regions & synonyms
│           └── HistoryModal.jsx      # SQLite query history drawer
│
├── models/                           # PyTorch ML Models & Cache
│   ├── broad_category_classifier_full.pt # Fine-tuned EfficientNet-B0
│   └── hf_cache/
│
├── services/                         # Core Machine Learning & External APIs
│   ├── local_classifier.py           # PyTorch broad category classifier
│   ├── explainability.py             # Grad-CAM activation heatmap generator
│   ├── api_huggingface.py            # HuggingFace Vision Transformers (ViT)
│   ├── api_plantnet.py               # Pl@ntNet Botany API integration
│   ├── api_gbif.py                   # GBIF taxonomy, coordinates & IUCN threat ratings
│   ├── api_inaturalist.py            # Taxon name mapping & resolution
│   ├── api_wikipedia.py              # Wikipedia structured section parser
│   ├── report_generator.py           # Markdown field dossier generator
│   └── db_handler.py                 # SQLite cache CRUD with auto-migrations
│
├── db/                               # Database Storage
│   └── species_cache.db              # SQLite persistent cache
│
├── tests/                            # Automated Test Suite (9 Tests)
│   ├── test_api_endpoints.py         # FastAPI endpoint integration tests
│   ├── test_explainability.py        # Grad-CAM heatmap generation tests
│   ├── test_api_gbif.py              # GBIF taxonomy, GIS coordinates & IUCN tests
│   ├── test_api_inaturalist.py       # iNaturalist name mapping tests
│   ├── test_api_wikipedia.py         # Wikipedia encyclopedia tests
│   └── test_report_generator.py      # Field dossier generator tests
│
├── app.py                            # Streamlit standalone dashboard
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## 🧪 Automated Testing

Run the full automated test suite covering ML inference, Grad-CAM generation, REST endpoints, GBIF GIS/IUCN APIs, and report generation:

```bash
python -m unittest discover tests
```

```
Ran 9 tests in 26.261s

OK
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
