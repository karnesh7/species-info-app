import React, { useState } from 'react';
import { 
  BookOpen, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  ShieldAlert, 
  MapPin, 
  Utensils, 
  Activity, 
  HelpCircle 
} from 'lucide-react';

const SECTION_ICONS = {
  'Conservation Status': <ShieldAlert size={16} style={{ color: 'var(--accent-amber)' }} />,
  'Habitat / Distribution': <MapPin size={16} style={{ color: 'var(--accent-mint)' }} />,
  'Diet': <Utensils size={16} style={{ color: 'var(--accent-blue)' }} />,
  'Behavior': <Activity size={16} style={{ color: 'var(--accent-purple)' }} />,
  'Also Known As': <HelpCircle size={16} style={{ color: 'var(--text-muted)' }} />
};

export default function WikipediaViewer({ wikipedia }) {
  if (!wikipedia) return null;

  const { summary, url, sections } = wikipedia;
  const sectionKeys = sections ? Object.keys(sections) : [];

  // Default open the first section if available
  const [openSections, setOpenSections] = useState({
    [sectionKeys[0] || '']: true
  });

  const toggleSection = (key) => {
    setOpenSections((prev) => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <div className="glass-card wiki-card">
      <div className="wiki-header">
        <div className="wiki-title">
          <BookOpen size={18} style={{ color: 'var(--accent-mint)' }} />
          <h3>Species Dossier & Encyclopedia</h3>
        </div>

        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="nav-link-btn"
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
          >
            <span>Read on Wikipedia</span>
            <ExternalLink size={12} />
          </a>
        )}
      </div>

      {summary && summary !== 'Not available' && (
        <p className="wiki-summary">{summary}</p>
      )}

      {sectionKeys.length > 0 && (
        <div className="section-accordion">
          {sectionKeys.map((heading) => {
            const isOpen = openSections[heading];
            const icon = SECTION_ICONS[heading] || <BookOpen size={16} />;

            return (
              <div key={heading} className="accordion-item">
                <button
                  type="button"
                  className="accordion-trigger"
                  onClick={() => toggleSection(heading)}
                >
                  <div className="accordion-trigger-left">
                    {icon}
                    <span>{heading}</span>
                  </div>
                  {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {isOpen && (
                  <div className="accordion-content">
                    <p style={{ whiteSpace: 'pre-line' }}>{sections[heading]}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
