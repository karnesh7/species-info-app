import React from 'react';
import { BarChart3 } from 'lucide-react';

export default function ConfidenceMeter({ scores }) {
  if (!scores || scores.length === 0) return null;

  return (
    <div className="glass-card score-card">
      <div className="score-title">
        <BarChart3 size={18} style={{ color: 'var(--accent-mint)' }} />
        <h3>Top Prediction Candidates</h3>
      </div>

      <div className="score-list">
        {scores.slice(0, 5).map((item, index) => {
          const percentage = (item.score * 100).toFixed(1);
          return (
            <div key={index} className="score-row">
              <div className="score-label-row">
                <span className="score-label-name" title={item.label}>
                  {item.label}
                </span>
                <span className="score-percentage">{percentage}%</span>
              </div>
              <div className="score-track">
                <div
                  className="score-fill"
                  style={{ width: `${Math.max(item.score * 100, 3)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
