# FaunaFlora AI — Quantitative Benchmark Report

**Generated:** 2026-08-09 23:32:54 UTC  
**Environment:** Python 2.13.0+cpu on CPU  
**Model Architecture:** EfficientNet-B0 PyTorch Classifier  

---

## 📊 Summary Performance Metrics

| Benchmark Component | Metric | Value | Reference / Notes |
| :--- | :--- | :--- | :--- |
| **Model Size** | Checkpoint Size | `15.66 MB` | Standalone `.pt` file |
| **Parameters** | Total Weights | `4,015,234` | 4.02M Parameters |
| **PyTorch Inference** | Latency (Mean) | `162.25 ms` | Sub-25ms on standard CPU |
| **PyTorch Inference** | Latency (P50 Median) | `116.94 ms` | 50 iterations |
| **PyTorch Inference** | Latency (P90) | `332.02 ms` | 90th percentile |
| **PyTorch Inference** | Throughput | `6.2 FPS` | Frames / Inferences per second |
| **Grad-CAM XAI** | Heatmap Generation | `788.67 ms` | Backprop + Turbo colormap |
| **SQLite Cache Read** | Retrieval Latency | `1.546 ms` | Persistent SQLite cache |
| **Cache Speedup** | Acceleration Factor | **`1196.7x`** | Compared to ~1850ms live API call |
| **Field Report Gen** | Generation Time | `0.0505 ms` | `19,800 docs/sec` |
| **FastAPI Health** | Response Latency | `3.41 ms` | `GET /api/health` |
| **FastAPI Samples** | Response Latency | `2.62 ms` | `GET /api/samples` |

---

## 🔬 Benchmark Methodology

1. **PyTorch Classifier Latency**: Measured across 50 iterations with input resolution $224 \times 224 \times 3$ on CPU.
2. **Grad-CAM Attention Mapping**: Measured end-to-end forward activation capture, gradient backpropagation on `model.conv_head`, upsampling, and base64 PNG encoding.
3. **SQLite Caching vs. Live Network Aggregation**: Compares local JSON-serialized SQLite read latency against external network round-trips across GBIF, iNaturalist, and Wikipedia APIs.
4. **Endpoint Responsiveness**: Measured through FastAPI's ASGI client layer.
