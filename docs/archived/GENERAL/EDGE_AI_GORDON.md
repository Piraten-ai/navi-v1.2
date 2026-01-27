# Edge AI for Gordon (Ingenioren) - System Engineer Role

## Overview

Gordon is the Ingenioren (System Engineer) module responsible for real-time hardware monitoring, fan control, and physics calculations. Currently uses Ollama (llama3.2), but for edge deployment we need lightweight alternatives that run efficiently on embedded systems.

## Recommended Edge AI Solutions

### 1. **ONNX Runtime** ⭐ RECOMMENDED
**Best for: System monitoring, lightweight inference, cross-platform**

```
Installation:
pip install onnxruntime-gpu  # or onnxruntime for CPU
```

**Pros:**
- Ultra-lightweight (MB footprint)
- Cross-platform (Windows, Linux, ARM, Jetson)
- GPU support (NVIDIA, AMD)
- Fast inference (10-50ms per request)
- Pre-trained models available
- Excellent for sequential monitoring

**Cons:**
- Requires pre-trained ONNX models
- Less flexible for custom tasks

**Use Case:**
- Real-time anomaly detection
- System health scoring
- Predictive maintenance (fan speed prediction)
- Performance trend analysis

**Example Models:**
- ResNet-based anomaly detection
- LSTM for time-series forecasting
- Lightweight classification models

---

### 2. **TensorFlow Lite** 
**Best for: Mobile/embedded, quantized models**

```
Installation:
pip install tensorflow-lite
```

**Pros:**
- Optimized for mobile/embedded
- 50-90% smaller than TensorFlow
- 1-3x faster inference
- Full model quantization support
- Good community and examples

**Cons:**
- Limited dynamic shape support
- Training requires TensorFlow → TFLite conversion

**Use Case:**
- Fan control predictions
- Thermal forecasting
- System stress classification

---

### 3. **OpenVINO** (Intel)
**Best for: x86/x64 systems, Intel CPU optimization**

```
Installation:
pip install openvino openvino-dev
```

**Pros:**
- Extreme optimization for Intel CPUs
- 2-10x faster than standard inference
- Excellent quantization tools
- Great documentation
- Model conversion tools

**Cons:**
- Primarily Intel-focused
- Setup more complex

**Use Case:**
- Lagrange/drift calculations
- Real-time system state estimation
- Complex physics simulations

---

### 4. **NVIDIA TensorRT**
**Best for: Jetson Nano/Xavier, NVIDIA GPU systems**

```
Installation:
pip install tensorrt
```

**Pros:**
- 10-40x faster than standard inference
- Perfect for Jetson hardware
- INT8 quantization
- Excellent for multi-model pipelines

**Cons:**
- NVIDIA-only
- Complex setup
- Requires CUDA

**Use Case:**
- Multi-model inference
- Real-time performance estimation
- GPU-accelerated computations

---

### 5. **MediaPipe**
**Best for: Vision/perception tasks**

```
Installation:
pip install mediapipe
```

**Pros:**
- Pre-built solutions
- Real-time performance
- Mobile-optimized
- Easy integration

**Cons:**
- Limited to perception tasks
- Less suitable for generic system monitoring

---

## Recommended Implementation for Gordon

### **Primary: ONNX Runtime**
- Lightweight (< 10MB)
- Fast (10-50ms inference)
- Cross-platform
- GPU support when available

### **Secondary: TensorFlow Lite**
- Backup solution
- Same performance characteristics
- Better ecosystem for retraining

---

## Integration with Gordon (Ingenioren)

### Current Architecture
```python
# Current: ollama.py
class GorillaOllama:
    def query_ollama(self, prompt):
        response = httpx.post(
            "http://192.168.39.196:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt}
        )
```

### Proposed: ONNX-based System Monitor
```python
import onnxruntime as ort
import numpy as np

class EdgeAISystemMonitor:
    def __init__(self):
        # Load pre-trained anomaly detection model
        self.session = ort.InferenceSession("models/system_anomaly_detector.onnx")
    
    def detect_anomalies(self, metrics: Dict[str, float]) -> Dict:
        """Detect system anomalies using edge AI"""
        # Prepare input: [CPU%, Memory%, Temp, Disk%, FanSpeed]
        input_data = np.array([[
            metrics['cpu_percent'],
            metrics['memory_percent'],
            metrics['temp_celsius'],
            metrics['disk_percent'],
            metrics['fan_speed']
        ]], dtype=np.float32)
        
        # Run inference
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        result = self.session.run([output_name], {input_name: input_data})
        
        return {
            'anomaly_score': float(result[0][0][0]),
            'is_anomaly': float(result[0][0][0]) > 0.7,
            'confidence': float(result[0][0][1])
        }
    
    def predict_fan_speed(self, current_metrics: Dict) -> int:
        """Predict optimal fan speed for current conditions"""
        # Load fan control model
        # Returns: 50-100% fan speed
        pass
    
    def forecast_thermal_trend(self, history: List[Dict]) -> Dict:
        """Forecast next 5 minutes thermal behavior"""
        # LSTM-based time series prediction
        pass
```

---

## Implementation Steps

### 1. Acquire/Train Models
```bash
# Option A: Use pre-trained models
python download_models.py

# Option B: Convert existing models
python convert_to_onnx.py --input model.pt --output model.onnx

# Option C: Quantize for smaller size
python quantize_model.py --model model.onnx --output model_quantized.onnx
```

### 2. Update ingenioren.py
```python
# Replace Ollama calls with ONNX
from edge_ai_monitor import EdgeAISystemMonitor

class Ingenioren:
    def __init__(self):
        self.ai_monitor = EdgeAISystemMonitor()
    
    async def get_extended_diagnostics(self):
        metrics = self.collect_metrics()
        
        # Use edge AI instead of Ollama
        anomalies = self.ai_monitor.detect_anomalies(metrics)
        fan_prediction = self.ai_monitor.predict_fan_speed(metrics)
        thermal_forecast = self.ai_monitor.forecast_thermal_trend(self.metric_history)
        
        return {
            'metrics': metrics,
            'ai_analysis': {
                'anomalies': anomalies,
                'fan_prediction': fan_prediction,
                'thermal_forecast': thermal_forecast
            }
        }
```

### 3. Update Frontend
```typescript
// No changes needed - same API interface
// But now faster response times due to edge AI

const handleAIAnalysis = async () => {
  const response = await fetch('/api/v1/ingenioren/diagnostics');
  const data = await response.json();
  
  // AI analysis now includes edge AI predictions
  console.log('Anomaly detection:', data.ai_analysis.anomalies);
  console.log('Fan prediction:', data.ai_analysis.fan_prediction);
};
```

---

## Model Options for System Monitoring

### Anomaly Detection
- **AutoEncoder ONNX**: Detects abnormal metric combinations
- **Isolation Forest**: Fast, lightweight anomaly scoring
- **Local Outlier Factor**: Density-based anomaly detection

### Fan Control
- **Gradient Boosting (XGBoost)**: Predict optimal fan speed
- **Neural Network (ONNX)**: Non-linear fan speed mapping
- **Lookup Tables + Interpolation**: Lightweight, fast

### Thermal Forecasting
- **LSTM (TensorFlow Lite)**: Time-series prediction
- **Exponential Smoothing**: Lightweight trend forecasting
- **Polynomial Regression**: Simple, fast, accurate

---

## Performance Comparison

| Solution | Model Size | Inference Time | Memory | Platform |
|----------|-----------|-----------------|--------|----------|
| Ollama   | 2-7GB     | 500ms-2s       | 2-4GB  | Linux/Mac|
| ONNX Runtime | <50MB   | 10-50ms        | 100MB  | All ✓    |
| TensorFlow Lite | 10-100MB | 20-100ms     | 200MB  | All ✓    |
| OpenVINO | 50-200MB  | 5-30ms         | 150MB  | x86/ARM  |
| TensorRT | 100-500MB | 2-20ms         | 500MB  | Jetson   |

---

## Recommended Path Forward

### Phase 1: Development (Now)
- Use ONNX Runtime + pre-trained models
- Keep Ollama for fallback
- Implement alongside existing Ollama integration

### Phase 2: Production (After testing)
- Remove Ollama dependency
- Deploy ONNX models to target system
- Monitor performance metrics

### Phase 3: Optimization
- Fine-tune models with real system data
- Implement model versioning
- Create CI/CD pipeline for model updates

---

## Getting Started

```python
# installation.py
import subprocess
import sys

def setup_edge_ai():
    """Setup edge AI for Gordon"""
    print("Installing ONNX Runtime...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "onnxruntime",
        "onnx",
        "scikit-learn"  # For anomaly detection models
    ])
    
    print("Downloading models...")
    # Download pre-trained ONNX models
    # https://github.com/onnx/models
    
    print("Edge AI setup complete!")

if __name__ == "__main__":
    setup_edge_ai()
```

---

## Files to Update

1. **backend/app/modules/ingenioren.py**
   - Add EdgeAISystemMonitor class
   - Replace Ollama calls with edge AI inference

2. **backend/app/models/edge_ai.py** (NEW)
   - ONNX model loading
   - Inference functions
   - Model caching

3. **requirements.txt**
   - Add onnxruntime

4. **docker-compose.yml**
   - Remove ollama service (optional)
   - Add ONNX model mounting

5. **.env.development**
   - Remove OLLAMA_BASE_URL (optional)
   - Add EDGE_AI_MODEL_PATH

---

## References

- ONNX Model Zoo: https://github.com/onnx/models
- ONNX Runtime: https://onnxruntime.ai/
- TensorFlow Lite: https://www.tensorflow.org/lite
- OpenVINO: https://docs.openvino.ai/
- TensorRT: https://docs.nvidia.com/deeplearning/tensorrt/

---

**Status**: Ready for implementation
**Priority**: High (improves performance, reduces resource usage)
**Estimated Development Time**: 3-5 days
