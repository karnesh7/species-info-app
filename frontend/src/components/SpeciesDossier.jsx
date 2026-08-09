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
  X,
  RotateCcw,
  Sliders
} from 'lucide-react';
import TaxonomyTree from './TaxonomyTree';
import ConfidenceMeter from './ConfidenceMeter';
import WikipediaViewer from './WikipediaViewer';
import OccurrenceMap from './OccurrenceMap';
import ExplainabilityViewer from './ExplainabilityViewer';
import ConservationBadge from './ConservationBadge';

const CATEGORY_META = [
  { id: 'Bird', label: 'Bird', sub: 'HuggingFace ViT', icon: <Bird size={14} /> },
  { id: 'Plant', label: 'Plant', sub: 'Pl@ntNet API', icon: <Leaf size={14} /> },
  { id: 'Mammal', label: 'Mammal', sub: 'General ViT', icon: <Sparkles size={14} /> },
  { id: 'Insect', label: 'Insect', sub: 'General ViT', icon: <Bug size={14} /> },
  { id: 'Fish', label: 'Fish', sub: 'General ViT', icon: <Fish size={14} /> },
  { id: 'Reptile_Amphibian', label: 'Reptile / Amphibian', sub: 'General ViT', icon: <ShieldCheck size={14} /> }
];

const CATEGORY_ICONS = {
  Bird: <Bird size={15} />,
  Fish: <Fish size={15} />,
  Insect: <Bug size={15} />,
  Mammal: <Sparkles size={15} />,
  Plant: <Leaf size={15} />,
  Reptile_Amphibian: <ShieldCheck size={15} />
};

export default function SpeciesDossier({ data, onReidentifyWithCategory, hasUploadedImage, previewUrl, loading }) {
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);

  if (!data) return null;

  const {
    common_name,
    scientific_name,
    category,
    confidence,
    category_confidence,
    is_low_confidence,
    is_category_overridden,
    warning_message,
    all_category_scores,
    model_scores,
    explainability,
    iucn_status,
    taxonomy,
    regions,
    coordinates,
    synonyms,
    wikipedia,
    cached,
    cached_at
  } = data;

  const wikiImage = wikipedia?.image;
  const categoryIcon = CATEGORY_ICONS[category] || <Sparkles size={15} />;

  return (
    <div className="dossier-area">
      {/* Low Confidence Warning Alert & Category Override Bar */}
      {is_low_confidence && warning_message && (
        <div className="alert-warning">
          <AlertTriangle size={20} />
          <div>
            <strong>Inference Advisory:</strong> {warning_message}
          </div>
        </div>
      )}

      {/* Manual Category Override Controls (Available when an image is uploaded) */}
      {hasUploadedImage && (
        <div className="glass-card" style={{ padding: '1.25rem 1.5rem', background: 'rgba(16, 185, 129, 0.04)', borderColor: is_low_confidence ? 'rgba(245, 158, 11, 0.4)' : 'var(--border-emerald)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 600, color: is_low_confidence ? '#fde68a' : 'var(--text-primary)' }}>
              <Sliders size={16} style={{ color: is_low_confidence ? 'var(--accent-amber)' : 'var(--accent-mint)' }} />
              <span>{is_low_confidence ? 'Model Uncertain — Select Broad Category to Re-Route' : 'Manually Override Broad Category Route'}</span>
            </div>
            {is_category_overridden && (
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-mint)', fontWeight: 600 }}>
                ✓ User Override Active
              </span>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(135px, 1fr))', gap: '0.5rem' }}>
            {CATEGORY_META.map((cat) => {
              const isSelected = category === cat.id;
              return (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => onReidentifyWithCategory(cat.id)}
                  disabled={loading}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    padding: '0.55rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-subtle)',
                    background: isSelected ? 'rgba(16, 185, 129, 0.2)' : 'var(--bg-card-glass)',
                    color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all var(--transition-fast)',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected && !loading) {
                      e.currentTarget.style.borderColor = 'var(--accent-primary)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected && !loading) {
                      e.currentTarget.style.borderColor = 'var(--border-subtle)';
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', fontWeight: 600 }}>
                    {cat.icon}
                    <span>{cat.label}</span>
                  </div>
                  <span style={{ fontSize: '0.68rem', color: isSelected ? 'var(--accent-mint)' : 'var(--text-muted)' }}>
                    {cat.sub}
                  </span>
                </button>
              );
            })}
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

            {iucn_status && iucn_status.code && (
              <span className="badge-category" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                <span>IUCN: {iucn_status.code}</span>
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

      {/* IUCN Red List Conservation Status Banner */}
      {iucn_status && (
        <ConservationBadge iucnStatus={iucn_status} />
      )}

      {/* AI Visual Explainability (Grad-CAM Attention Heatmap) */}
      {explainability && (
        <ExplainabilityViewer explainability={explainability} originalImage={previewUrl} />
      )}

      {/* Broad Category Distribution Meter (if multi-class scores exist) */}
      {all_category_scores && all_category_scores.length > 0 && (
        <div className="glass-card score-card">
          <div className="score-title">
            <Sliders size={18} style={{ color: 'var(--accent-mint)' }} />
            <h3>PyTorch Broad Category Probabilities</h3>
          </div>
          <div className="score-list">
            {all_category_scores.map((item, index) => {
              const percentage = (item.confidence * 100).toFixed(1);
              const isTop = index === 0;
              return (
                <div key={index} className="score-row">
                  <div className="score-label-row">
                    <span className="score-label-name" style={{ fontWeight: isTop ? 700 : 500, color: isTop ? 'var(--accent-mint)' : 'var(--text-primary)' }}>
                      {item.category.replace('_', ' / ')} {isTop ? '(Top Model Pick)' : ''}
                    </span>
                    <span className="score-percentage">{percentage}%</span>
                  </div>
                  <div className="score-track">
                    <div
                      className="score-fill"
                      style={{ 
                        width: `${Math.max(item.confidence * 100, 2)}%`,
                        background: isTop 
                          ? 'linear-gradient(90deg, var(--accent-primary), var(--accent-mint))'
                          : 'rgba(255, 255, 255, 0.25)'
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Species Candidate Predictions Meter (if image classification was used) */}
      {model_scores && model_scores.length > 0 && (
        <ConfidenceMeter scores={model_scores} />
      )}

      {/* Visual Biological Hierarchy Tree */}
      <TaxonomyTree taxonomy={taxonomy} />

      {/* Wikipedia Encyclopedia Summary & Sections */}
      <WikipediaViewer wikipedia={wikipedia} />

      {/* GBIF Occurrence Sightings Map, Regions & Scientific Synonyms */}
      <OccurrenceMap regions={regions} coordinates={coordinates} synonyms={synonyms} commonName={common_name} />

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
