# FaunaFlora AI — Species Identification & Biodiversity Intelligence

An enterprise-grade, full-stack AI system that identifies biological species from images or taxonomy queries using a **hierarchical multi-stage inference pipeline**, data enrichment from GBIF & Wikipedia, and high-performance SQLite caching.

Featuring a decoupled **FastAPI** asynchronous REST backend and a modern **React + Vite** glassmorphic web application.

---

## 🌟 Key Architecture Highlights

```
                          [User Uploads Specimen Photo]
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │ Stage 1: PyTorch Classifier  │  <-- Fast Coarse Triage
                         │    (EfficientNet-B0 Model)   │      (~15ms CPU inference)
                         └──────────────┬───────────────┘
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
                         ┌──────────────────────────────┐
                         │ Stage 3: Name Normalization  │  <-- iNaturalist Taxa API
                         │  (Common <-> Scientific)     │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │   Multi-Tier SQLite Cache    │  <-- <5ms cached response
                         │    (db/species_cache.db)     │
                         └──────┬───────────────┬───────┘
                           HIT  │               │ MISS
                                │               ▼
                                │    ┌─────────────────────────┐
                                │    │ GBIF Taxonomy & Regions │
                                │    │ Wikipedia Encyclopedia  │
                                │    └──────────┬──────────────┘
                                │               │
                                └───────┬───────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │    Modern React + Vite UI    │
                         │    & Swagger REST API Docs   │
                         └──────────────────────────────┘
```

---

## 🚀 Features

* **Multi-Stage AI Pipeline**: First triages images into 6 broad kingdoms/classes via local PyTorch EfficientNet-B0 before routing to specialized Vision Transformers or botany APIs.
* **Modern Glassmorphic Frontend**: Responsive dark nature theme, interactive specimen dropzone, camera capture, animated pipeline stepper, visual taxonomy tree, and candidate confidence meters.
* **FastAPI Asynchronous Backend**: Clean REST endpoints with Pydantic v2 data validation, CORS middleware, and automated OpenAPI/Swagger documentation (`/docs`).
* **Automated Biological Enrichment**: Resolves scientific classification (Kingdom → Species) via GBIF, retrieves recorded occurrence regions, synonyms, and structured Wikipedia encyclopedic dossiers (Diet, Habitat, Behavior, Conservation).
* **Multi-Tier SQLite Caching**: Eliminates redundant API calls and external rate limits with persistent local caching.
* **Dual Interface Support**: Run either the flagship **React+Vite Modern Web UI** or the standalone **Streamlit** dashboard.

---

## 🧑‍💻 Technology Stack

| Layer | Technologies / Libraries |
| :--- | :--- |
| **Frontend** | React 18, Vite 5, Lucide Icons, Glassmorphic CSS System |
| **Backend REST API** | FastAPI, Uvicorn, Pydantic v2, Python-Multipart |
| **Machine Learning** | PyTorch, Torchvision (EfficientNet-B0), HuggingFace Transformers (ViT), Pl@ntNet API |
| **Data Enrichment** | GBIF Occurrence & Species API, iNaturalist Taxa API, Wikipedia & Wikipedia-API |
| **Database / Cache** | SQLite3 (Persistent JSON-serialized cache) |
| **Alternative UI** | Streamlit |

---

## 🛠️ Setup Instructions

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/karnesh7/species-info-app.git
cd species-info-app

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
PLANTNET_API_KEY=your_plantnet_api_key_here
HF_TOKEN=your_huggingface_token_here
```

---

## 🏃 Running the Application

### Option 1: Modern Full-Stack Web App (Recommended)

**Terminal 1 — Start the FastAPI Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```
> Interactive API Documentation available at: **http://localhost:8000/docs**

**Terminal 2 — Start the React Frontend:**
```bash
cd frontend
npm install
npm run dev
```
> Access the modern web interface at: **http://localhost:5173**

---

### Option 2: Production Single-Server Bundle

Build the frontend bundle once and serve everything directly from FastAPI:

```bash
cd frontend
npm run build
cd ..
uvicorn api.main:app --port 8000
```
> Access the full-stack app at: **http://localhost:8000**

---

### Option 3: Streamlit Interface (Legacy Runner)

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
species-info-app/
├── api/                              # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                       # REST endpoints & CORS configuration
│   └── schemas.py                    # Pydantic v2 validation models
│
├── frontend/                         # Modern React + Vite Web App
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx                   # Central state & pipeline orchestrator
│       ├── index.css                 # Glassmorphic nature design system
│       └── components/
│           ├── Header.jsx            # Navigation bar & doc links
│           ├── SampleChips.jsx       # 1-click exploration showcase
│           ├── Dropzone.jsx          # Drag-and-drop & camera input
│           ├── PipelineStatus.jsx    # Real-time multi-stage stepper
│           ├── SpeciesDossier.jsx    # Hero species card & status badges
│           ├── TaxonomyTree.jsx      # Visual hierarchy (Kingdom -> Species)
│           ├── ConfidenceMeter.jsx   # Top-5 candidate prediction bars
│           ├── WikipediaViewer.jsx   # Tabbed encyclopedic sections
│           ├── OccurrenceMap.jsx     # GBIF recorded regions & synonyms
│           └── HistoryModal.jsx      # SQLite query history drawer
│
├── models/                           # PyTorch classifiers & cache
│   ├── broad_category_classifier_full.pt
│   └── hf_cache/
│
├── services/                         # Reusable ML & API Integration Services
│   ├── local_classifier.py           # PyTorch EfficientNet inference
│   ├── api_huggingface.py            # HuggingFace ViT models
│   ├── api_plantnet.py               # Pl@ntNet botany API
│   ├── api_gbif.py                   # GBIF taxonomy & occurrences
│   ├── api_inaturalist.py            # Scientific name mapping
│   ├── api_wikipedia.py              # Wikipedia structured sections
│   └── db_handler.py                 # SQLite cache CRUD handlers
│
├── db/                               # SQLite database
│   └── species_cache.db
│
├── tests/                            # Unit & Integration Tests
│   ├── test_api_endpoints.py
│   ├── test_api_gbif.py
│   ├── test_api_inaturalist.py
│   └── test_api_wikipedia.py
│
├── app.py                            # Streamlit alternative interface
└── requirements.txt                  # Python dependencies
```

---

## 🧠 Local Classifier Details

* **Architecture**: Fine-tuned **EfficientNet-B0** exported as a PyTorch `.pt` model.
* **Categories**: `Bird`, `Fish`, `Insect`, `Mammal`, `Plant`, `Reptile_Amphibian`.
* **Validation Accuracy**: **~96%** with sub-20ms latency.
* **Colab Notebook**: 📓 [Train Classifier on Google Colab](https://colab.research.google.com/github/karnesh7/species-info-app/blob/main/notebooks/train_classifier.ipynb)

---

## 🧪 Testing

Run all unit and integration tests:

```bash
python -m unittest discover tests
```

---

## 📄 License

[MIT](LICENSE)
