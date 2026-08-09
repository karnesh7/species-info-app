import React, { useState } from 'react';
import { 
  Bird, 
  Fish, 
  Bug, 
  Sparkles, 
  Leaf, 
  ShieldCheck, 
  AlertTriangle, 
  Database, 
  Clock, 
  Maximize2,
  X
} from 'lucide-react';
import TaxonomyTree from './TaxonomyTree';
import ConfidenceMeter from './ConfidenceMeter';
import WikipediaViewer from './WikipediaViewer';
import OccurrenceMap from './OccurrenceMap';

const CATEGORY_ICONS = {
  Bird: <Bird size={15} />,
  Fish: <Fish size={15} />,
  Insect: <Bug size={15} />,
  Mammal: <Sparkles size={15} />,
  Plant: <Leaf size={15} />,
  Reptile_Amphibian: <ShieldCheck size={15} />
};

export default function SpeciesDossier({ data }) {
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);

  if (!data) return null;

  const {
    common_name,
    scientific_name,
    category,
    confidence,
    category_confidence,
    is_low_confidence,
    warning_message,
    model_scores,
    taxonomy,
    regions,
    synonyms,
    wikipedia,
    cached,
    cached_at
  } = data;

  const wikiImage = wikipedia?.image;
  const categoryIcon = CATEGORY_ICONS[category] || <Sparkles size={15} />;

  return (
    <div className="dossier-area">
      {/* Low Confidence Warning Alert */}
      {is_low_confidence && warning_message && (
        <div className="alert-warning">
          <AlertTriangle size={20} />
          <div>
            <strong>Inference Advisory:</strong> {warning_message}
          </div>
        </div>
      )}

      {/* Hero Dossier Card */}
      <div className="glass-card dossier-hero">
        {wikiImage ? (
          <div 
            className="hero-media-wrapper"
            style={{ cursor: 'pointer' }}
            onClick={() => setIsImageModalOpen(true)}
            title="Click to view full image"
          >
            <img 
              src={wikiImage} 
              alt={common_name} 
              className="hero-media-img" 
            />
            <div style={{ position: 'absolute', bottom: '8px', right: '8px' }}>
              <div className="icon-btn" style={{ width: '28px', height: '28px' }}>
                <Maximize2 size={13} />
              </div>
            </div>
          </div>
        ) : (
          <div className="hero-media-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(16, 185, 129, 0.05)' }}>
            <Leaf size={48} style={{ color: 'var(--accent-mint)', opacity: 0.5 }} />
          </div>
        )}

        <div className="hero-dossier-content">
          <div className="dossier-badges">
            {category && (
              <span className="badge-category">
                {categoryIcon}
                <span>{category.replace('_', ' / ')}</span>
              </span>
            )}

            {category_confidence && (
              <span className="badge-category" style={{ background: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-blue)', borderColor: 'rgba(56, 189, 248, 0.3)' }}>
                <span>Model Confidence: {(category_confidence * 100).toFixed(0)}%</span>
              </span>
            )}

            {cached ? (
              <span className="badge-cache" title={`Cached from SQLite on ${cached_at || 'previous session'}`}>
                <Database size={12} />
                <span>SQLite Cached (&lt;5ms)</span>
              </span>
            ) : (
              <span className="badge-cache" style={{ background: 'rgba(16, 185, 129, 0.12)', color: 'var(--accent-mint)', borderColor: 'var(--border-emerald)' }}>
                <Clock size={12} />
                <span>Live Enriched</span>
              </span>
            )}
          </div>

          <div>
            <h2 className="dossier-common-name">{common_name}</h2>
            <div className="dossier-scientific-name">{scientific_name}</div>
          </div>

          {cached_at && (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Cached on: {new Date(cached_at).toLocaleString()}
            </div>
          )}
        </div>
      </div>

      {/* Model Predictions Meter (if image classification was used) */}
      {model_scores && model_scores.length > 0 && (
        <ConfidenceMeter scores={model_scores} />
      )}

      {/* Visual Biological Hierarchy Tree */}
      <TaxonomyTree taxonomy={taxonomy} />

      {/* Wikipedia Encyclopedia Summary & Sections */}
      <WikipediaViewer wikipedia={wikipedia} />

      {/* GBIF Occurrence Regions & Scientific Synonyms */}
      <OccurrenceMap regions={regions} synonyms={synonyms} />

      {/* Image Modal */}
      {isImageModalOpen && wikiImage && (
        <div className="modal-backdrop" onClick={() => setIsImageModalOpen(false)}>
          <div style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }} onClick={(e) => e.stopPropagation()}>
            <img 
              src={wikiImage} 
              alt={common_name} 
              style={{ width: '100%', maxHeight: '85vh', objectFit: 'contain', borderRadius: 'var(--radius-md)' }} 
            />
            <button 
              className="icon-btn" 
              style={{ position: 'absolute', top: '10px', right: '10px' }}
              onClick={() => setIsImageModalOpen(false)}
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
