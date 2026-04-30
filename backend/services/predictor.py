import math
import time


base_weights = {
    "mobile": 0.4,
    "cctv": 0.7,
    "transaction": 0.9
}


def is_valid_coordinate(lat, lng):
    return isinstance(lat, (int, float)) and isinstance(lng, (int, float))


def get_default_confidence(t):
    if t == "mobile":
        return 0.6
    if t == "cctv":
        return 0.85
    if t == "transaction":
        return 0.9
    return 0.5


def time_decay(signal_time):
    now = time.time() * 1000
    diff = (now - signal_time) / 1000
    decay = math.exp(-diff / (3600 * 24))
    return max(decay, 0.1)


def get_weight(signal):
    return math.sqrt(
        (base_weights.get(signal["type"], 0.5)) *
        (signal.get("confidence", 0.5))
    ) * time_decay(signal["time"])


def predict_location(signals):

    processed = []

    for s in signals:
        if is_valid_coordinate(s["lat"], s["lng"]) and s.get("time"):
            processed.append({
                **s,
                "confidence": s.get("confidence") or get_default_confidence(s.get("type", "mobile"))
            })

    # --- HANDLE CASES ---
    if len(processed) == 0:
        return None

    if len(processed) == 1:
        s = processed[0]
        return {
            "lat": s["lat"],
            "lng": s["lng"],
            "confidence": 0.7,
            "radius": 200,
            "mostInfluential": s.get("type", "mobile"),
            "signalsUsed": 1,
            "heatmap": [[s["lat"], s["lng"], 1.0]]
        }

    # SORT BY TIME
    processed.sort(key=lambda x: x["time"])

    # --- WEIGHTED FUSION ---
    sum_lat = sum_lng = total_weight = 0

    for s in processed:
        w = get_weight(s)
        sum_lat += s["lat"] * w
        sum_lng += s["lng"] * w
        total_weight += w

    fusion_lat = sum_lat / total_weight
    fusion_lng = sum_lng / total_weight

    # --- SPREAD ---
    weighted_distance_sum = 0

    for s in processed:
        dlat = s["lat"] - fusion_lat
        dlng = s["lng"] - fusion_lng
        dist = math.sqrt(dlat**2 + dlng**2) * 111000

        weighted_distance_sum += dist * get_weight(s)

    avg_distance = weighted_distance_sum / total_weight

    # --- VELOCITY MODEL ---
    recent = processed[-4:]

    total_vlat = total_vlng = count = 0

    for i in range(1, len(recent)):
        dt = (recent[i]["time"] - recent[i - 1]["time"]) / 1000
        if dt == 0:
            continue

        total_vlat += (recent[i]["lat"] - recent[i - 1]["lat"]) / dt
        total_vlng += (recent[i]["lng"] - recent[i - 1]["lng"]) / dt
        count += 1

    velocity_lat = total_vlat / count if count else 0
    velocity_lng = total_vlng / count if count else 0

    speed = math.sqrt(velocity_lat**2 + velocity_lng**2) * 111000

    # SPEED CAP
    MAX_SPEED = 20
    scale = 1 if speed <= MAX_SPEED else MAX_SPEED / speed

    last = recent[-1]
    now = time.time() * 1000
    delta_time = (now - last["time"]) / 1000

    predicted_lat = last["lat"] + velocity_lat * delta_time * scale
    predicted_lng = last["lng"] + velocity_lng * delta_time * scale

    # --- BLEND ---
    predicted_lat = 0.6 * predicted_lat + 0.4 * fusion_lat
    predicted_lng = 0.6 * predicted_lng + 0.4 * fusion_lng

    # 🔥 CONTROLLED RADIUS (FIXED)
    time_hours = delta_time / 3600

    base_radius = 200 + 800 * (1 - math.exp(-time_hours))
    radius = min(base_radius * (1 + time_hours * 0.3), 1500)

    # --- CONFIDENCE ---
    recency_factor = math.exp(-delta_time / 3600)
    consistency_factor = 1 / (1 + avg_distance / 1000)

    confidence = min(1, 0.4 + recency_factor * consistency_factor)

    # --- MOST INFLUENTIAL ---
    max_signal = max(processed, key=lambda s: get_weight(s))

    # 🔥 HEATMAP
    heatmap = []
    for s in processed:
        heatmap.append([
            s["lat"],
            s["lng"],
            get_weight(s)
        ])

    return {
        "lat": predicted_lat,
        "lng": predicted_lng,
        "confidence": round(confidence, 2),
        "radius": int(radius),
        "mostInfluential": max_signal["type"],
        "signalsUsed": len(processed),
        "heatmap": heatmap
    }