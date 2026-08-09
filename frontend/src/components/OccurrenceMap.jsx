import React from 'react';
import { Globe, Bookmark } from 'lucide-react';
import InteractiveMap from './InteractiveMap';

export default function OccurrenceMap({ regions, coordinates, synonyms, commonName }) {
  const hasCoordinates = coordinates && coordinates.length > 0;
  const hasRegions = regions && regions.length > 0;
  const hasSynonyms = synonyms && synonyms.length > 0;

  if (!hasRegions && !hasSynonyms && !hasCoordinates) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Interactive Global Sighting Map */}
      {hasCoordinates && (
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div className="regions-header" style={{ marginBottom: '1rem' }}>
            <div className="regions-title">
              <Globe size={18} style={{ color: 'var(--accent-blue)' }} />
              <h3>Global Biodiversity Sightings</h3>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>GBIF Live Observation Coordinates</span>
          </div>

          <InteractiveMap coordinates={coordinates} commonName={commonName} />
        </div>
      )}

      {/* Regions & Synonyms Grid */}
      {(hasRegions || hasSynonyms) && (
        <div style={{ display: 'grid', gridTemplateColumns: hasRegions && hasSynonyms ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
          {hasRegions && (
            <div className="glass-card regions-card">
              <div className="regions-header">
                <div className="regions-title">
                  <Globe size={18} style={{ color: 'var(--accent-blue)' }} />
                  <h3>Recorded Occurrence Countries</h3>
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
      )}
    </div>
  );
}
