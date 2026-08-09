import React from 'react';
import { Sparkles, Database, FileCode2, ExternalLink, Leaf } from 'lucide-react';

export default function Header({ onOpenHistory }) {
  return (
    <header className="navbar">
      <div className="brand-logo">
        <div className="logo-icon-wrapper">
          <Leaf size={22} />
        </div>
        <span>FaunaFlora<span style={{ color: 'var(--accent-mint)' }}>.ai</span></span>
      </div>

      <div className="nav-actions">
        <div className="nav-badge">
          <Sparkles size={14} />
          <span>Dual ML + Full-Stack</span>
        </div>

        <button 
          id="btn-open-history"
          className="nav-link-btn" 
          onClick={onOpenHistory}
          title="View cached queries from SQLite"
        >
          <Database size={15} />
          <span>Cache History</span>
        </button>

        <a 
          href="http://localhost:8000/docs" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="nav-link-btn"
          title="Open FastAPI Swagger Interactive Docs"
        >
          <FileCode2 size={15} />
          <span>API Docs</span>
          <ExternalLink size={12} />
        </a>
      </div>
    </header>
  );
}
