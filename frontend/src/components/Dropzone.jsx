import React, { useRef, useState } from 'react';
import { UploadCloud, Camera, X, Image as ImageIcon } from 'lucide-react';

export default function Dropzone({ selectedFile, previewUrl, onFileSelect, onClearFile, disabled }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        onFileSelect(file);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div>
      {/* Hidden Inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/jpg"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      {previewUrl ? (
        <div className="preview-wrapper">
          <img src={previewUrl} alt="Upload preview" className="preview-img" />
          <div className="preview-overlay">
            <button
              type="button"
              className="icon-btn"
              onClick={onClearFile}
              disabled={disabled}
              title="Remove image"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      ) : (
        <div
          className={`dropzone ${isDragOver ? 'active' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
        >
          <div className="dropzone-icon">
            <UploadCloud size={28} />
          </div>
          <div>
            <div className="dropzone-text">Drop specimen photo here, or browse</div>
            <div className="dropzone-hint">Supports JPEG, JPG, PNG (up to 15MB)</div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
            <button
              type="button"
              className="nav-link-btn"
              onClick={(e) => {
                e.stopPropagation();
                if (!disabled) cameraInputRef.current?.click();
              }}
              title="Take a photo with device camera"
            >
              <Camera size={14} />
              <span>Camera</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
