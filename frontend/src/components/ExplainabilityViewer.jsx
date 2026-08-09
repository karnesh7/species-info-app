import React, { useState } from 'react';
import { Eye, Layers, Sparkles, Info, Sliders } from 'lucide-react';

export default function ExplainabilityViewer({ explainability, originalImage }) {
  if (!explainability) return null;

  const { overlay_image, heatmap_image, target_category, confidence, description } = explainability;
  const [viewMode, setViewMode] = useState('overlay'); // 'overlay' | 'original' | 'heatmap'
  const [overlayOpacity, setOverlayOpacity] = useState(55); // percentage for custom blend

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '1.5rem', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div className="logo-icon-wrapper" style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #a855f7, #6366f1)' }}>
            <Eye size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', margin: 0 }}>AI Visual Explainability (Grad-CAM)</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Gradient-Weighted Class Activation Mapping on ConvHead Layer
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span className="badge-category" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', borderColor: 'rgba(168, 85, 247, 0.3)' }}>
            <Sparkles size={12} />
            <span>Target: {target_category}</span>
          </span>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <button
          type="button"
          className={`nav-link-btn ${viewMode === 'overlay' ? 'active' : ''}`}
          style={{
            background: viewMode === 'overlay' ? 'rgba(16, 185, 129, 0.2)' : 'var(--bg-card-glass)',
            color: viewMode === 'overlay' ? '#ffffff' : 'var(--text-secondary)',
            borderColor: viewMode === 'overlay' ? 'var(--accent-primary)' : 'var(--border-subtle)'
          }}
          onClick={() => setViewMode('overlay')}
        >
          <Layers size={14} />
          <span>Blended Overlay</span>
        </button>

        <button
          type="button"
          className={`nav-link-btn ${viewMode === 'heatmap' ? 'active' : ''}`}
          style={{
            background: viewMode === 'heatmap' ? 'rgba(168, 85, 247, 0.2)' : 'var(--bg-card-glass)',
            color: viewMode === 'heatmap' ? '#ffffff' : 'var(--text-secondary)',
            borderColor: viewMode === 'heatmap' ? '#a855f7' : 'var(--border-subtle)'
          }}
          onClick={() => setViewMode('heatmap')}
        >
          <Eye size={14} />
          <span>Raw Heatmap Mask</span>
        </button>

        {originalImage && (
          <button
            type="button"
            className={`nav-link-btn ${viewMode === 'original' ? 'active' : ''}`}
            style={{
              background: viewMode === 'original' ? 'rgba(56, 189, 248, 0.2)' : 'var(--bg-card-glass)',
              color: viewMode === 'original' ? '#ffffff' : 'var(--text-secondary)',
              borderColor: viewMode === 'original' ? 'var(--accent-blue)' : 'var(--border-subtle)'
            }}
            onClick={() => setViewMode('original')}
          >
            <span>Original Specimen</span>
          </button>
        )}
      </div>

      {/* Visual Canvas Container */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(220px, 320px) 1fr', gap: '1.5rem', alignItems: 'center' }}>
        <div style={{ position: 'relative', width: '100%', height: '240px', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--border-emerald)', boxShadow: '0 8px 24px rgba(0,0,0,0.5)', background: '#000000' }}>
          {viewMode === 'original' && originalImage && (
            <img src={originalImage} alt="Original Specimen" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          )}

          {viewMode === 'heatmap' && (
            <img src={heatmap_image} alt="Grad-CAM Heatmap" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          )}

          {viewMode === 'overlay' && (
            <div style={{ position: 'relative', width: '100%', height: '100%' }}>
              {/* Base image */}
              {originalImage ? (
                <img src={originalImage} alt="Base" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain' }} />
              ) : (
                <img src={overlay_image} alt="Overlay" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              )}
              {/* Heatmap blend */}
              {originalImage && (
                <img
                  src={heatmap_image}
                  alt="Heatmap layer"
                  style={{
                    position: 'absolute',
                    inset: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    opacity: overlayOpacity / 100,
                    mixBlendMode: 'screen'
                  }}
                />
              )}
            </div>
          )}
        </div>

        {/* Explainability Explanation & Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {viewMode === 'overlay' && originalImage && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Sliders size={13} style={{ color: 'var(--accent-mint)' }} /> Heatmap Opacity
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-mint)' }}>{overlayOpacity}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="90"
                value={overlayOpacity}
                onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-primary)', cursor: 'pointer' }}
              />
            </div>
          )}

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem', padding: '0.85rem 1rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.55 }}>
            <Info size={18} style={{ color: 'var(--accent-blue)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Feature Attribution Interpretation:</strong>
              <p style={{ marginTop: '0.25rem', color: 'var(--text-secondary)' }}>
                {description}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', fontSize: '0.75rem' }}>
                <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }}></span>
                <span>Warm / Red: High Activation</span>
                <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: '#3b82f6', marginLeft: '0.5rem' }}></span>
                <span>Cold / Blue: Low Activation</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
