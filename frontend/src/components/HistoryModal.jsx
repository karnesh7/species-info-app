import React from 'react';
import { X, Database, ChevronRight, Leaf } from 'lucide-react';

export default function HistoryModal({ isOpen, onClose, historyItems, onSelectHistoryItem }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Database size={18} style={{ color: 'var(--accent-mint)' }} />
            <h3 style={{ fontSize: '1.15rem' }}>SQLite Cache Queries</h3>
          </div>
          <button className="icon-btn" onClick={onClose} title="Close modal">
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {historyItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              No cached species found yet. Run an identification to store records in SQLite!
            </div>
          ) : (
            historyItems.map((item, idx) => (
              <div
                key={idx}
                className="history-item"
                onClick={() => {
                  onSelectHistoryItem(item.scientific_name);
                  onClose();
                }}
              >
                <div className="history-item-left">
                  {item.thumbnail ? (
                    <img src={item.thumbnail} alt={item.common_name || item.scientific_name} className="history-thumb" />
                  ) : (
                    <div className="history-thumb" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(16, 185, 129, 0.1)' }}>
                      <Leaf size={16} style={{ color: 'var(--accent-mint)' }} />
                    </div>
                  )}
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                      {item.common_name || item.scientific_name}
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontStyle: 'italic', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {item.scientific_name}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  {item.cached_at && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {new Date(item.cached_at).toLocaleDateString()}
                    </span>
                  )}
                  <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
