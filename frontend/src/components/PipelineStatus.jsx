import React from 'react';
import { Cpu, CheckCircle2, Loader2, Workflow } from 'lucide-react';

const PIPELINE_STAGES = [
  { id: 1, label: 'Broad Category Triage (PyTorch EfficientNet-B0)' },
  { id: 2, label: 'Domain Specialist Model (ViT / Pl@ntNet API)' },
  { id: 3, label: 'Taxonomy & Name Resolution (iNaturalist API)' },
  { id: 4, label: 'Biodiversity Data & Occurrence Search (GBIF)' },
  { id: 5, label: 'Encyclopedic Knowledge Extraction (Wikipedia)' }
];

export default function PipelineStatus({ currentStep }) {
  return (
    <div className="stepper-card">
      <div className="stepper-title">
        <Workflow size={16} />
        <span>Multi-Stage Inference Pipeline</span>
      </div>

      <div className="stepper-steps">
        {PIPELINE_STAGES.map((stage) => {
          const isCompleted = currentStep > stage.id;
          const isActive = currentStep === stage.id;

          return (
            <div
              key={stage.id}
              className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
            >
              <div className="step-bullet">
                {isCompleted ? (
                  <CheckCircle2 size={13} />
                ) : isActive ? (
                  <Loader2 size={13} className="spinner" />
                ) : (
                  stage.id
                )}
              </div>
              <span>{stage.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
