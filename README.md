# Missing Person Tracker

A real-time location prediction system that uses image EXIF data to estimate the most probable location of a missing person.

## 🚀 Features

- Upload multiple images
- Extract GPS + timestamp from EXIF data
- Upload Transaction details (for trial a json file is included in /backend/transactions.json)
- Upload Mobile Signal details (for trial a json file is included in /backend/mobile_signals.json)
- Time-weighted prediction (recent images prioritized)
- Heatmap visualization
- Confidence score with animated UI
- Controlled radius prediction (no unrealistic expansion)
- Clear/reset functionality

---
---

## 🧠 How It Works

1. Extract GPS + timestamp from images
2. Apply time-decay weighting (recent data = higher importance)
3. Compute fused location + movement prediction
4. Generate:
   - Most probable location
   - Heatmap density
   - Confidence score
   - Search radius

---

## 📁 Project Structure

```
backend/
  main.py
  services/
    predictor.py

frontend/
  index.html
```

---

## ⚙️ Installation

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run backend

```
cd backend
uvicorn main:app --reload

cd D:\Missing-Person
.\venv\Scripts\activate
pip install uvicorn fastapi
cd D:\Missing-Person\backend
uvicorn main:app --reload
```

### 3. Open frontend

Open `frontend/index.html` in browser
            (OR)
http://127.0.0.1:8000/

---

## 📦 Requirements

- fastapi
- uvicorn
- pillow
- numpy
- python-multipart

---

## ⚠️ Important Notes

- Use **original camera images**
- Images from WhatsApp or screenshots may not contain GPS data
- If no GPS → no map output

---

## 🎯 Demo Flow

1. Upload images
2. View prediction + heatmap
3. Check confidence & radius
4. Click "Clear" to reset

---

## 🧩 Future Improvements

- Real-time tracking
- Multi-person support
- Road-aware movement prediction
- CCTV / transaction data fusion

---

## 👨‍💻 Author

- Robin Ponnanna K M
- Pancham Verm
- Prashanth K
- Utkarsh Singh
