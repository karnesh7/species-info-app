import React from 'react';
import { Compass } from 'lucide-react';

export default function SampleChips({ samples, onSelectSample, disabled }) {
  if (!samples || samples.length === 0) return null;

  return (
    <section className="sample-section">
      <div className="sample-title-row">
        <span className="sample-label">
          <Compass size={14} /> Quick Exploration Showcase
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Click any specimen for instant inference & enrichment
        </span>
      </div>

      <div className="sample-grid">
        {samples.map((sample) => (
          <button
            key={sample.scientific_name}
            className="sample-card"
            onClick={() => onSelectSample(sample.name)}
            disabled={disabled}
            title={`${sample.name} (${sample.scientific_name}) — ${sample.description}`}
          >
            {sample.sample_image && (
              <img 
                src={sample.sample_image} 
                alt={sample.name} 
                className="sample-card-img" 
                loading="lazy"
              />
            )}
            <div className="sample-info">
              <span className="sample-name">{sample.name}</span>
              <span className="sample-tag">{sample.tag}</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
