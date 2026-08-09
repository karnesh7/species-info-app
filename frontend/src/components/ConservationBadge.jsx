import React from 'react';
import { ShieldAlert, ShieldCheck, Shield, ExternalLink, HelpCircle } from 'lucide-react';

const IUCN_TIERS = [
  { code: 'EX', label: 'Extinct', color: '#475569', bg: 'rgba(71, 85, 105, 0.25)', border: '#64748b' },
  { code: 'EW', label: 'Extinct in Wild', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.2)', border: '#c084fc' },
  { code: 'CR', label: 'Critically Endangered', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.25)', border: '#f87171' },
  { code: 'EN', label: 'Endangered', color: '#f43f5e', bg: 'rgba(244, 63, 94, 0.25)', border: '#fb7185' },
  { code: 'VU', label: 'Vulnerable', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.25)', border: '#fbbf24' },
  { code: 'NT', label: 'Near Threatened', color: '#eab308', bg: 'rgba(234, 179, 8, 0.2)', border: '#fde047' },
  { code: 'LC', label: 'Least Concern', color: '#10b981', bg: 'rgba(16, 185, 129, 0.2)', border: '#34d399' },
  { code: 'DD', label: 'Data Deficient', color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.2)', border: '#cbd5e1' },
  { code: 'NE', label: 'Not Evaluated', color: '#64748b', bg: 'rgba(100, 116, 139, 0.2)', border: '#94a3b8' }
];

export default function ConservationBadge({ iucnStatus }) {
  if (!iucnStatus || (!iucnStatus.code && !iucnStatus.category)) {
    return null;
  }

  const rawCode = (iucnStatus.code || '').trim().toUpperCase();
  const rawCat = (iucnStatus.category || '').trim().toUpperCase();

  // Normalize string for exact token matching
  const normalize = (str) => (str || '').toUpperCase().replace(/[^A-Z]/g, '');

  // Exact matching algorithm to prevent substring false matches (e.g. DATA_DEFICIENT matching EN)
  const activeTier = IUCN_TIERS.find((t) => {
    if (rawCode && t.code === rawCode) return true;
    if (rawCat) {
      const normCat = normalize(rawCat);
      const normLabel = normalize(t.label);
      return normCat === normLabel || normCat === t.code;
    }
    return false;
  }) || {
    code: rawCode || 'DD',
    label: iucnStatus.category || 'Data Deficient',
    color: '#94a3b8',
    bg: 'rgba(148, 163, 184, 0.2)',
    border: '#cbd5e1'
  };

  const isThreatened = ['CR', 'EN', 'VU', 'EW', 'EX'].includes(activeTier.code);
  const isDataDeficient = ['DD', 'NE'].includes(activeTier.code);

  return (
    <div className="glass-card" style={{ padding: '1.25rem', marginBottom: '1.5rem', border: `1px solid ${activeTier.border}44` }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div
            className="logo-icon-wrapper"
            style={{
              width: '32px',
              height: '32px',
              background: activeTier.bg,
              color: activeTier.color,
              border: `1px solid ${activeTier.border}`
            }}
          >
            {isThreatened ? <ShieldAlert size={18} /> : isDataDeficient ? <HelpCircle size={18} /> : <ShieldCheck size={18} />}
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', margin: 0 }}>IUCN Red List Conservation Status</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Official Global Biodiversity Assessment
            </span>
          </div>
        </div>

        {iucnStatus.iucn_url && (
          <a
            href={iucnStatus.iucn_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline"
            style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem', textDecoration: 'none' }}
          >
            <span>IUCN Assessment</span>
            <ExternalLink size={12} />
          </a>
        )}
      </div>

      {/* Spectrum Meter Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(60px, 1fr))', gap: '0.35rem', marginBottom: '1rem' }}>
        {IUCN_TIERS.map((tier) => {
          const isActive = tier.code === activeTier.code;
          return (
            <div
              key={tier.code}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '0.45rem 0.15rem',
                borderRadius: '8px',
                background: isActive ? tier.bg : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${isActive ? tier.border : 'rgba(255, 255, 255, 0.06)'}`,
                boxShadow: isActive ? `0 0 16px ${tier.color}44` : 'none',
                transform: isActive ? 'scale(1.05)' : 'scale(1)',
                transition: 'all 0.2s ease',
                textAlign: 'center'
              }}
            >
              <span style={{ fontSize: '0.82rem', fontWeight: 800, color: isActive ? tier.color : 'var(--text-muted)' }}>
                {tier.code}
              </span>
              <span style={{ fontSize: '0.58rem', color: isActive ? '#ffffff' : 'var(--text-muted)', marginTop: '2px', display: 'block', lineHeight: 1.1 }}>
                {tier.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Description Callout */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          background: activeTier.bg,
          border: `1px solid ${activeTier.border}33`,
          fontSize: '0.85rem',
          color: '#f8fafc'
        }}
      >
        <span style={{ fontWeight: 700, color: activeTier.color }}>
          Status: {activeTier.label} ({activeTier.code})
        </span>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
          • Official assessment on the IUCN Red List of Threatened Species.
        </span>
      </div>
    </div>
  );
}
