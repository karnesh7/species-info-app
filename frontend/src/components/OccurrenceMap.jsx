import React from 'react';
import { Globe, Bookmark } from 'lucide-react';

export default function OccurrenceMap({ regions, synonyms }) {
  const hasRegions = regions && regions.length > 0;
  const hasSynonyms = synonyms && synonyms.length > 0;

  if (!hasRegions && !hasSynonyms) return null;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: hasRegions && hasSynonyms ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
      {hasRegions && (
        <div className="glass-card regions-card">
          <div className="regions-header">
            <div className="regions-title">
              <Globe size={18} style={{ color: 'var(--accent-blue)' }} />
              <h3>Recorded Occurrence Regions</h3>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>GBIF Observation Facets</span>
          </div>

          <div className="region-tags">
            {regions.map((region, idx) => (
              <span key={idx} className="region-pill">
                <Globe size={12} style={{ color: 'var(--accent-blue)', opacity: 0.7 }} />
                <span>{region}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {hasSynonyms && (
        <div className="glass-card synonyms-card">
          <div className="synonyms-title">
            <Bookmark size={18} style={{ color: 'var(--accent-purple)' }} />
            <h3>Scientific Synonyms</h3>
          </div>

          <div className="synonyms-list">
            {synonyms.map((syn, idx) => (
              <span key={idx} className="synonym-pill" title="Alternative or historic scientific synonym">
                {syn}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
