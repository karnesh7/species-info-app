import React, { useState } from 'react';
import { Download, Printer, Copy, Check, X, FileText, Sparkles } from 'lucide-react';

export default function ExportDossierModal({ isOpen, onClose, data }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !data) return null;

  const {
    common_name,
    scientific_name,
    category,
    confidence,
    iucn_status,
    taxonomy,
    regions,
    synonyms,
    wikipedia,
    model_scores
  } = data;

  // Generate Markdown Text
  const generateMarkdown = () => {
    const lines = [];
    lines.push(`# Biological Specimen Field Dossier: ${common_name}`);
    lines.push(`**Scientific Name:** *${scientific_name}*  `);
    lines.push(`**Broad Category:** ${category || 'General'}  `);
    lines.push(`**Compiled:** ${new Date().toUTCString()}  `);
    lines.push(`**Engine:** FaunaFlora AI Multi-Stage Biological Pipeline\n`);
    lines.push(`---\n`);

    // 1. Conservation
    lines.push(`## 🛡️ IUCN Red List Conservation Status`);
    if (iucn_status && (iucn_status.code || iucn_status.category)) {
      lines.push(`- **Threat Rating:** **${iucn_status.category || ''} (${iucn_status.code || ''})**`);
      if (iucn_status.iucn_url) {
        lines.push(`- **Official Assessment:** [View on IUCN Red List](${iucn_status.iucn_url})`);
      }
    } else {
      lines.push(`- *Status not assessed or data deficient.*`);
    }
    lines.push(``);

    // 2. Taxonomy
    lines.push(`## 🧬 Biological Taxonomy (GBIF)`);
    if (taxonomy && typeof taxonomy === 'object' && Object.keys(taxonomy).length > 0) {
      lines.push(`| Taxonomic Rank | Classification |`);
      lines.push(`| :--- | :--- |`);
      ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species'].forEach((rank) => {
        if (taxonomy[rank]) {
          lines.push(`| **${rank.charAt(0).toUpperCase() + rank.slice(1)}** | *${taxonomy[rank]}* |`);
        }
      });
    } else {
      lines.push(`- *Taxonomy data not available.*`);
    }
    lines.push(``);

    // 3. Model Predictions
    if (model_scores && model_scores.length > 0) {
      lines.push(`## 🎯 ML Model Candidate Predictions`);
      lines.push(`| Candidate Species | Confidence Score |`);
      lines.push(`| :--- | :--- |`);
      model_scores.slice(0, 5).forEach((item) => {
        lines.push(`| ${item.label} | ${(item.score * 100).toFixed(1)}% |`);
      });
      lines.push(``);
    }

    // 4. Wikipedia
    if (wikipedia) {
      lines.push(`## 📖 Natural History & Encyclopedic Knowledge`);
      if (wikipedia.summary && wikipedia.summary !== 'Not available') {
        lines.push(`### Summary\n${wikipedia.summary}\n`);
      }
      if (wikipedia.sections) {
        Object.entries(wikipedia.sections).forEach(([h, c]) => {
          lines.push(`### ${h}\n${c}\n`);
        });
      }
      if (wikipedia.url) {
        lines.push(`**Reference:** [Read full Wikipedia article](${wikipedia.url})\n`);
      }
    }

    // 5. Regions & Synonyms
    if (regions && regions.length > 0) {
      lines.push(`## 🌍 Recorded Occurrence Regions`);
      lines.push(regions.join(', '));
      lines.push(``);
    }

    if (synonyms && synonyms.length > 0) {
      lines.push(`## 🏷️ Scientific Synonyms`);
      synonyms.slice(0, 10).forEach((s) => lines.push(`- *${s}*`));
      lines.push(``);
    }

    lines.push(`---\n*Report compiled autonomously by FaunaFlora AI Intelligence System.*`);
    return lines.join('\n');
  };

  const mdText = generateMarkdown();

  // 1. Download .md File
  const handleDownloadMarkdown = () => {
    const blob = new Blob([mdText], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${scientific_name.replace(/\s+/g, '_').toLowerCase()}_field_dossier.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 2. Print / Save as PDF
  const handlePrintPDF = () => {
    window.print();
  };

  // 3. Copy to Clipboard
  const handleCopy = () => {
    navigator.clipboard.writeText(mdText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="glass-card"
        style={{
          width: '90%',
          maxWidth: '680px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          padding: '1.75rem',
          border: '1px solid var(--border-emerald)',
          boxShadow: '0 20px 50px rgba(0,0,0,0.6)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div className="logo-icon-wrapper" style={{ width: '36px', height: '36px', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-mint))' }}>
              <FileText size={18} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.2rem', margin: 0 }}>Export Specimen Field Dossier</h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {common_name} ({scientific_name})
              </span>
            </div>
          </div>

          <button className="icon-btn" onClick={onClose} aria-label="Close export modal">
            <X size={18} />
          </button>
        </div>

        {/* Action Buttons Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <button type="button" className="btn-primary" onClick={handleDownloadMarkdown} style={{ justifyContent: 'center' }}>
            <Download size={16} />
            <span>Download .MD</span>
          </button>

          <button type="button" className="btn-outline" onClick={handlePrintPDF} style={{ justifyContent: 'center' }}>
            <Printer size={16} />
            <span>Print / Save PDF</span>
          </button>

          <button type="button" className="btn-outline" onClick={handleCopy} style={{ justifyContent: 'center' }}>
            {copied ? <Check size={16} style={{ color: 'var(--accent-mint)' }} /> : <Copy size={16} />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Markdown'}</span>
          </button>
        </div>

        {/* Markdown Document Preview */}
        <div style={{ flex: 1, overflowY: 'auto', background: 'rgba(0, 0, 0, 0.4)', borderRadius: 'var(--radius-md)', padding: '1rem', border: '1px solid var(--border-subtle)' }}>
          <pre style={{ margin: 0, fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: '#94a3b8', whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
            {mdText}
          </pre>
        </div>
      </div>
    </div>
  );
}
