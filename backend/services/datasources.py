from datetime import datetime
from typing import Optional
from backend.models.schemas import LocationSignal


class DataSource:
    def fetch_signals(self, person_id: str, since: Optional[datetime] = None) -> list[LocationSignal]:
        raise NotImplementedError


class MobileDataSource(DataSource):
    def __init__(self, db_path: str = "data/mobile_signals.db"):
        self.db_path = db_path

    def fetch_signals(self, person_id: str, since: Optional[datetime] = None) -> list[LocationSignal]:
        return []

    def add_signal(self, signal: LocationSignal):
        pass


class CCTVDataSource(DataSource):
    def __init__(self, db_path: str = "data/cctv.db"):
        self.db_path = db_path

    def fetch_signals(self, person_id: str, since: Optional[datetime] = None) -> list[LocationSignal]:
        return []


class TransactionDataSource(DataSource):
    def __init__(self, db_path: str = "data/transactions.db"):
        self.db_path = db_path

    def fetch_signals(self, person_id: str, since: Optional[datetime] = None) -> list[LocationSignal]:
        return []


class WiFiDataSource(DataSource):
    def __init__(self, db_path: str = "data/wifi.db"):
        self.db_path = db_path

    def fetch_signals(self, person_id: str, since: Optional[datetime] = None) -> list[LocationSignal]:
        return []


class DataSourceIntegrator:
    def __init__(self):
        self.sources = {
            "mobile": MobileDataSource(),
            "cctv": CCTVDataSource(),
            "transaction": TransactionDataSource(),
            "wifi": WiFiDataSource()
        }

    def fetch_all_signals(self, person_id: str, since: Optional[datetime] = None) -> list[LocationSignal]:
        all_signals = []
        for source_name, source in self.sources.items():
            signals = source.fetch_signals(person_id, since)
            all_signals.extend(signals)
        return sorted(all_signals, key=lambda s: s.timestamp)

    def add_signal(self, signal: LocationSignal):
        source = self.sources.get(signal.source)
        if source:
            source.add_signal(signal)


integrator = DataSourceIntegrator()