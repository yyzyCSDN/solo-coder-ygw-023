class DomainRules:
    """Frame and point-map input validation."""
    @staticmethod
    def frame_checksum(payload: bytes) -> int: return sum(payload)%256
    @staticmethod
    def validate_point_map(mapping: dict) -> dict:
        if not mapping: raise ValueError("empty point map")
        for point,row in mapping.items():
            if not point or "address" not in row: raise ValueError("point address is required")
        return mapping
    @staticmethod
    def normalize_station(value: str) -> str:
        value=value.strip().upper()
        if not value: raise ValueError("station is required")
        return value
