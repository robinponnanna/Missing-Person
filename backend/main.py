from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime
import json
import io
from uuid import uuid4
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

signals_db = []

def load_json_data(filename):
    file_path = BACKEND_DIR / filename
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return []

def dms_to_decimal(values, ref):
    try:
        d, m, s = [float(x) for x in values]
        result = d + (m / 60.0) + (s / 3600.0)
        return -result if ref in ['S', 'W'] else result
    except: return None

def extract_exif(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif = img._getexif()
        if not exif: return None
        data = {TAGS.get(k): v for k, v in exif.items()}
        gps = data.get("GPSInfo")
        if not gps: return None
        gps_data = {GPSTAGS.get(k): v for k, v in gps.items()}
        lat = dms_to_decimal(gps_data['GPSLatitude'], gps_data.get('GPSLatitudeRef', 'N'))
        lng = dms_to_decimal(gps_data['GPSLongitude'], gps_data.get('GPSLongitudeRef', 'E'))
        dt_str = data.get("DateTimeOriginal")
        ts = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S").timestamp() if dt_str else datetime.now().timestamp()
        return {"lat": lat, "lng": lng, "time": ts, "src": "GPS"}
    except: return None

def predict_location(signals):
    if not signals:
        return {
            "lat": 0, "lng": 0, "confidence": 0, 
            "radius": 0, "source": "N/A"
        }
    
    # Sort to get the latest activity
    sorted_s = sorted(signals, key=lambda x: x.get('time', 0), reverse=True)
    latest = sorted_s[0]
    
    # Calculate dynamic confidence (more signals = higher confidence)
    base_conf = 0.75
    signal_bonus = min(len(signals) * 0.02, 0.20)
    final_conf = base_conf + signal_bonus

    return {
        "lat": latest["lat"],
        "lng": latest["lng"],
        "confidence": round(final_conf, 2), # Returns 0.95, etc.
        "radius": 120,
        "source": latest.get("src", "Unknown")
    }

@app.post("/upload/images")
async def upload_images(files: list[UploadFile] = File(...)):
    for file in files:
        data = extract_exif(await file.read())
        if data: signals_db.append(data)
    return {"added": len(signals_db)}

@app.get("/track/mobile")
async def track_mobile(number: str = None):
    data = load_json_data("mobile_signals.json")
    points = [{"lat": s["lat"], "lng": s["lng"], "time": datetime.fromisoformat(s["timestamp"]).timestamp(), "src": "Tower", "id": s.get("mobile_no")} for s in data]
    if number: points = [p for p in points if number in str(p['id'])]
    return {"points": points, "predicted": predict_location(points)}

@app.get("/track/transactions")
async def track_bank(account: str = None):
    data = load_json_data("transactions.json")
    points = [{"lat": s["lat"], "lng": s["lng"], "time": datetime.fromisoformat(s["timestamp"]).timestamp(), "src": "Bank", "id": s.get("account_id")} for s in data]
    if account: points = [p for p in points if account in str(p['id'])]
    return {"points": points, "predicted": predict_location(points)}

@app.get("/track/omni")
async def track_omni():
    # 1. Collect Image GPS data from in-memory DB
    gps = [{"lat": s["lat"], "lng": s["lng"], "time": s["time"], "src": "GPS"} for s in signals_db]
    
    # 2. Collect 1000 records from mobile_signals.json
    mob_raw = load_json_data("mobile_signals.json")
    mobile = [{"lat": s["lat"], "lng": s["lng"], "time": datetime.fromisoformat(s["timestamp"]).timestamp(), "src": "Tower", "id": s.get("mobile_no")} for s in mob_raw]
    
    # 3. Collect 1000 records from transactions.json
    bank_raw = load_json_data("transactions.json")
    bank = [{"lat": s["lat"], "lng": s["lng"], "time": datetime.fromisoformat(s["timestamp"]).timestamp(), "src": "Bank", "id": s.get("account_id")} for s in bank_raw]

    # 4. Merge all sources into one massive dataset for the map
    all_points = gps + mobile + bank
    
    # 5. Calculate the most probable location based on the absolute latest hit
    return {"points": all_points, "predicted": predict_location(all_points)}

@app.get("/")
async def root(): return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/track/images")
async def track_images_only():
    """Isolates only the GPS metadata from uploaded images"""
    points = [{"lat": s["lat"], "lng": s["lng"], "time": s["time"], "src": "GPS"} for s in signals_db]
    points.sort(key=lambda x: x["time"], reverse=True)
    return {"points": points, "predicted": predict_location(points)}

@app.post("/clear")
async def clear_data():
    signals_db.clear()
    return {"status": "success"}

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")