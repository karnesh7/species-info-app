from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ModelScore(BaseModel):
    label: str
    score: float

class CategoryScore(BaseModel):
    category: str
    confidence: float

class CategoryPrediction(BaseModel):
    category: str
    confidence: float
    is_low_confidence: bool = False
    all_scores: List[CategoryScore] = []

class WikipediaInfo(BaseModel):
    summary: Optional[str] = "Not available"
    image: Optional[str] = None
    url: Optional[str] = None
    sections: Dict[str, str] = {}

class SpeciesDetailResponse(BaseModel):
    common_name: str
    scientific_name: str
    category: Optional[str] = None
    confidence: Optional[float] = None
    category_confidence: Optional[float] = None
    is_low_confidence: bool = False
    is_category_overridden: bool = False
    warning_message: Optional[str] = None
    all_category_scores: List[CategoryScore] = []
    model_scores: List[ModelScore] = []
    taxonomy: Dict[str, Any] = {}
    regions: List[str] = []
    synonyms: List[str] = []
    habitats: List[str] = []
    wikipedia: WikipediaInfo
    cached: bool = False
    cached_at: Optional[str] = None
    source: str = "live"

class SampleSpeciesItem(BaseModel):
    name: str
    scientific_name: str
    category: str
    tag: str
    description: str
    sample_image: Optional[str] = None

class HistoryItem(BaseModel):
    scientific_name: str
    common_name: Optional[str] = None
    category: Optional[str] = None
    cached_at: Optional[str] = None
    thumbnail: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    models_ready: bool
    db_connected: bool
    version: str = "1.0.0"
