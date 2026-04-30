# To run the system:

## 1. Install Python
- Download from https://python.org (Python 3.11+)
- During install, check "Add Python to PATH"

## 2. Install dependencies
```powershell
cd C:\Users\neuro\OneDrive\Desktop\hackathon
pip install fastapi uvicorn numpy scipy pydantic websockets
```

## 3. Start the backend
```powershell
cd backend
uvicorn main:app --reload
```

## 4. Open frontend
- Open `frontend/index.html` in your browser (double-click or drag to browser)

## 5. Generate demo data
- Visit http://localhost:8000/demo/generate in browser

## Demo workflow:
1. Start backend (`uvicorn main:app --reload`)
2. Open `frontend/index.html` in browser  
3. Visit `http://localhost:8000/demo/generate` to generate test signals
4. Refresh the frontend - you'll see demo person "John Doe" with location path on map