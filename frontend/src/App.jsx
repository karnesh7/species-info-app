import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Search, 
  Leaf, 
  AlertCircle, 
  Layers, 
  ArrowRight,
  RefreshCw
} from 'lucide-react';

import Header from './components/Header';
import SampleChips from './components/SampleChips';
import Dropzone from './components/Dropzone';
import PipelineStatus from './components/PipelineStatus';
import SpeciesDossier from './components/SpeciesDossier';
import HistoryModal from './components/HistoryModal';

const API_BASE = ''; // Uses Vite proxy in development, direct paths in production

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [speciesNameInput, setSpeciesNameInput] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [speciesData, setSpeciesData] = useState(null);
  
  const [samples, setSamples] = useState([]);
  const [historyItems, setHistoryItems] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Fetch samples and history on mount
  useEffect(() => {
    fetchSamples();
    fetchHistory();
  }, []);

  const fetchSamples = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/samples`);
      if (res.ok) {
        const data = await res.json();
        setSamples(data);
      }
    } catch (err) {
      console.warn('Failed to load sample species:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history`);
      if (res.ok) {
        const data = await res.json();
        setHistoryItems(data);
      }
    } catch (err) {
      console.warn('Failed to load history:', err);
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setSpeciesNameInput('');
    setError(null);
  };

  const handleClearFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  const animateSteps = (targetStep = 5) => {
    let step = 1;
    setCurrentStep(step);
    const interval = setInterval(() => {
      step += 1;
      if (step <= targetStep) {
        setCurrentStep(step);
      } else {
        clearInterval(interval);
      }
    }, 600);
    return interval;
  };

  const handleIdentify = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile && !speciesNameInput.trim()) {
      setError('Please upload an image specimen or enter a species name to identify.');
      return;
    }

    setLoading(true);
    setError(null);
    const stepTimer = animateSteps(selectedFile ? 5 : 4);

    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append('image', selectedFile);
      }
      if (speciesNameInput.trim()) {
        formData.append('species_name', speciesNameInput.trim());
      }

      const response = await fetch(`${API_BASE}/api/identify`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      clearInterval(stepTimer);

      if (!response.ok) {
        throw new Error(result.detail || 'Identification failed. Please try another image or name.');
      }

      setCurrentStep(6);
      setSpeciesData(result);
      fetchHistory(); // Refresh history cache
    } catch (err) {
      clearInterval(stepTimer);
      setError(err.message);
    } finally {
      setLoading(false);
      setTimeout(() => setCurrentStep(0), 1000);
    }
  };

  const handleSelectSampleOrHistory = async (speciesName) => {
    setLoading(true);
    setError(null);
    handleClearFile();
    setSpeciesNameInput(speciesName);
    const stepTimer = animateSteps(4);

    try {
      const response = await fetch(`${API_BASE}/api/species/${encodeURIComponent(speciesName)}`);
      const result = await response.json();
      clearInterval(stepTimer);

      if (!response.ok) {
        throw new Error(result.detail || `Failed to fetch data for ${speciesName}`);
      }

      setCurrentStep(6);
      setSpeciesData(result);
      fetchHistory();
    } catch (err) {
      clearInterval(stepTimer);
      setError(err.message);
    } finally {
      setLoading(false);
      setTimeout(() => setCurrentStep(0), 1000);
    }
  };

  return (
    <div className="app-container">
      <Header onOpenHistory={() => setIsHistoryOpen(true)} />

      {/* Hero Header */}
      <section className="hero-header">
        <div className="hero-pill">
          <Sparkles size={14} />
          <span>Multi-Stage Hierarchical AI Pipeline</span>
        </div>
        <h1 className="hero-title">Species Intelligence & Identification</h1>
        <p className="hero-subtitle">
          Identify flora and fauna from imagery or biological taxonomy. Powered by PyTorch local category triage,
          Vision Transformers, Pl@ntNet, iNaturalist, GBIF biodiversity backbone, and Wikipedia enrichment.
        </p>
      </section>

      {/* Quick Exploration Showcase Chips */}
      <SampleChips
        samples={samples}
        onSelectSample={handleSelectSampleOrHistory}
        disabled={loading}
      />

      {/* Main Workspace (Input Panel + Output Dossier) */}
      <div className="main-workspace">
        {/* Left: Input Panel */}
        <aside className="glass-card input-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Layers size={18} style={{ color: 'var(--accent-mint)' }} />
              <h3>Specimen Input</h3>
            </div>
            {speciesData && (
              <button
                type="button"
                className="nav-link-btn"
                style={{ fontSize: '0.8rem', padding: '0.3rem 0.65rem' }}
                onClick={() => {
                  setSpeciesData(null);
                  handleClearFile();
                  setSpeciesNameInput('');
                  setError(null);
                }}
              >
                <RefreshCw size={12} />
                <span>Reset</span>
              </button>
            )}
          </div>

          {/* Dropzone */}
          <Dropzone
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            onFileSelect={handleFileSelect}
            onClearFile={handleClearFile}
            disabled={loading}
          />

          <div className="search-divider">Or Query By Taxonomy</div>

          {/* Text Input Form */}
          <form onSubmit={handleIdentify} className="search-form">
            <input
              type="text"
              className="search-input"
              placeholder="e.g. Panthera leo, Bald Eagle, Monstera..."
              value={speciesNameInput}
              onChange={(e) => {
                setSpeciesNameInput(e.target.value);
                if (selectedFile) handleClearFile();
              }}
              disabled={loading}
            />
          </form>

          {/* Submit Button */}
          <button
            type="button"
            className="btn-primary btn-full"
            onClick={handleIdentify}
            disabled={loading || (!selectedFile && !speciesNameInput.trim())}
          >
            {loading ? (
              <>
                <div className="spinner" />
                <span>Analyzing Pipeline...</span>
              </>
            ) : (
              <>
                <Search size={16} />
                <span>Identify & Enrich Specimen</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>

          {/* Error Banner */}
          {error && (
            <div className="alert-warning" style={{ background: 'rgba(244, 63, 94, 0.12)', borderColor: 'rgba(244, 63, 94, 0.35)', color: '#fecdd3' }}>
              <AlertCircle size={18} style={{ color: 'var(--accent-rose)' }} />
              <div>{error}</div>
            </div>
          )}

          {/* Pipeline Stepper (Active during inference) */}
          {loading && <PipelineStatus currentStep={currentStep} />}
        </aside>

        {/* Right: Output Dossier Area */}
        <main>
          {speciesData ? (
            <SpeciesDossier data={speciesData} />
          ) : (
            <div className="glass-card empty-state">
              <div className="empty-icon">
                <Leaf size={32} />
              </div>
              <h2 className="empty-title">Ready for Specimen Analysis</h2>
              <p className="empty-desc">
                Upload an image or enter any common/scientific species name to initiate the multi-stage 
                classification pipeline and generate a biological dossier.
              </p>
            </div>
          )}
        </main>
      </div>

      {/* SQLite History Modal */}
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        historyItems={historyItems}
        onSelectHistoryItem={handleSelectSampleOrHistory}
      />
    </div>
  );
}
