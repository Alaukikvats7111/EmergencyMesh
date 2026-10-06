def classify(flame: int, smoke: int, rain: int, sound: int) -> tuple[str, str]:
    if flame:
        return "FIRE", "CRITICAL"

    if smoke:
        return "SMOKE", "CRITICAL"

    if rain and sound:
        return "FLOOD_SOUND", "HIGH"

    if rain:
        return "FLOOD_WARNING", "WARNING"

    if sound:
        return "EMERGENCY_SOUND", "WARNING"

    return "CLEAR", "NORMAL"


def severity_rank(s: str) -> int:
    return {
        "NORMAL": 0,
        "WARNING": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }.get(s, 0)