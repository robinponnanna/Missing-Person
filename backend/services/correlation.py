from datetime import datetime, timedelta
from typing import Optional
from backend.models.schemas import LocationSignal, LocationEstimate


class SignalCorrelator:
    def __init__(self, time_window_minutes: int = 30):
        self.time_window = timedelta(minutes=time_window_minutes)

    def correlate_signals(self, signals: list[LocationSignal]) -> list[LocationSignal]:
        if not signals:
            return []

        correlated = []
        signals = sorted(signals, key=lambda s: s.timestamp)
        window_start = signals[0].timestamp

        for signal in signals:
            if signal.timestamp - window_start <= self.time_window:
                correlated.append(signal)
            else:
                window_start = signal.timestamp
                correlated = [signal]

        return correlated

    def deduplicate(self, signals: list[LocationSignal], distance_threshold_m: float = 100) -> list[LocationSignal]:
        if not signals:
            return []

        unique = [signals[0]]

        for signal in signals[1:]:
            is_duplicate = False
            for ref in unique:
                if self._distance_m(signal.latitude, signal.longitude, ref.latitude, ref.longitude) < distance_threshold_m:
                    if signal.confidence >= ref.confidence:
                        unique.remove(ref)
                        unique.append(signal)
                        is_duplicate = True
                        break
            if not is_duplicate:
                unique.append(signal)

        return unique

    def _distance_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        import math
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class ConfidenceScorer:
    SOURCE_WEIGHTS = {
        "mobile": 0.7,
        "cctv": 0.9,
        "transaction": 0.8,
        "wifi": 0.75
    }

    def calculate_confidence(self, signals: list[LocationSignal]) -> float:
        if not signals:
            return 0.0

        total_weight = 0.0
        total_confidence = 0.0

        for signal in signals:
            weight = self.SOURCE_WEIGHTS.get(signal.source, 0.5)
            total_weight += weight
            total_confidence += signal.confidence * weight

        base_confidence = total_confidence / total_weight if total_weight > 0 else 0

        recency = self._recency_bonus(signals)
        density = self._density_bonus(signals)

        final_confidence = min(100, base_confidence * 0.7 + recency * 0.2 + density * 0.1)
        return final_confidence

    def _recency_bonus(self, signals: list[LocationSignal]) -> float:
        if not signals:
            return 0.0

        latest = max(signals, key=lambda s: s.timestamp) if signals else None
        if not latest:
            return 0.0

        age_hours = (datetime.now() - latest.timestamp).total_seconds() / 3600
        if age_hours < 1:
            return 100
        elif age_hours < 6:
            return 80
        elif age_hours < 24:
            return 60
        else:
            return 40

    def _density_bonus(self, signals: list[LocationSignal]) -> float:
        if len(signals) >= 5:
            return 100
        elif len(signals) >= 3:
            return 75
        elif len(signals) >= 1:
            return 50
        return 25


correlator = SignalCorrelator()
scorer = ConfidenceScorer()