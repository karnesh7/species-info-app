import React from 'react';
import { GitFork } from 'lucide-react';

const TAXONOMY_ORDER = [
  { key: 'kingdom', label: 'Kingdom' },
  { key: 'phylum', label: 'Phylum' },
  { key: 'class', label: 'Class' },
  { key: 'order', label: 'Order' },
  { key: 'family', label: 'Family' },
  { key: 'genus', label: 'Genus' },
  { key: 'species', label: 'Species' }
];

export default function TaxonomyTree({ taxonomy }) {
  if (!taxonomy || typeof taxonomy !== 'object' || Object.keys(taxonomy).length === 0) {
    return null;
  }

  const hasAnyRank = TAXONOMY_ORDER.some(({ key }) => Boolean(taxonomy[key]));
  if (!hasAnyRank) return null;

  return (
    <div className="glass-card taxonomy-card">
      <div className="taxonomy-header">
        <div className="taxonomy-title">
          <GitFork size={18} style={{ color: 'var(--accent-mint)' }} />
          <h3>Biological Classification (GBIF)</h3>
        </div>
        <span className="taxonomy-source">GBIF Taxonomic Backbone</span>
      </div>

      <div className="taxonomy-grid">
        {TAXONOMY_ORDER.map(({ key, label }) => {
          const value = taxonomy[key];
          if (!value) return null;

          return (
            <div key={key} className="taxonomy-pill">
              <span className="taxonomy-rank">{label}</span>
              <span className="taxonomy-value" title={value}>{value}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
