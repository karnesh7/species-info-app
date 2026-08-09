import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { MapPin, Globe, Compass } from 'lucide-react';

export default function InteractiveMap({ coordinates, commonName }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (!coordinates || coordinates.length === 0) return;

    // Clean up existing map instance if any
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    // Default center
    const defaultCenter = [coordinates[0].lat, coordinates[0].lng];
    const map = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: 3,
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: false
    });

    mapInstanceRef.current = map;

    // Dark Matter CartoDB Basemap Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18,
      subdomains: 'abcd'
    }).addTo(map);

    const latLngs = [];

    // Custom Glowing Emerald Circle Markers
    coordinates.forEach((pt) => {
      if (typeof pt.lat === 'number' && typeof pt.lng === 'number') {
        const marker = L.circleMarker([pt.lat, pt.lng], {
          radius: 7,
          fillColor: '#10b981',
          color: '#34d399',
          weight: 2,
          opacity: 0.9,
          fillOpacity: 0.75
        }).addTo(map);

        const popupContent = `
          <div style="font-family: 'Inter', sans-serif; color: #0f172a; padding: 4px; min-width: 150px;">
            <div style="font-weight: 700; color: #064e3b; font-size: 13px; margin-bottom: 2px;">
              📍 ${pt.country || 'Observation Sighting'}
            </div>
            <div style="font-size: 11px; color: #475569; margin-bottom: 4px;">
              ${pt.locality ? pt.locality : 'Recorded biological specimen'}
            </div>
            ${pt.year ? `<div style="font-size: 10px; font-weight: 600; color: #059669;">🗓️ Recorded in ${pt.year}</div>` : ''}
            <div style="font-size: 9px; color: #94a3b8; margin-top: 3px; font-family: monospace;">
              ${pt.lat.toFixed(3)}°, ${pt.lng.toFixed(3)}°
            </div>
          </div>
        `;

        marker.bindPopup(popupContent);
        latLngs.push([pt.lat, pt.lng]);
      }
    });

    // Auto-fit map bounds if points exist
    if (latLngs.length > 0) {
      const bounds = L.latLngBounds(latLngs);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 8 });
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [coordinates]);

  if (!coordinates || coordinates.length === 0) return null;

  const uniqueCountries = new Set(coordinates.map((c) => c.country).filter(Boolean)).size;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-mint)' }}>
          <Compass size={16} />
          <span>Global Specimen Sightings Map</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          <strong>{coordinates.length}</strong> georeferenced records across <strong>{uniqueCountries}</strong> countries (GBIF)
        </span>
      </div>

      <div
        ref={mapContainerRef}
        style={{
          width: '100%',
          height: '320px',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid var(--border-emerald)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
          background: '#0a0f0d'
        }}
      />
    </div>
  );
}
