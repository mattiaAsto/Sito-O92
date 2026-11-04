import re

_DMS = re.compile(
    r"""(?P<deg>\d+(?:[.,]\d+)?)\s*°\s*
        (?:(?P<min>\d+(?:[.,]\d+)?)\s*['′’‘]\s*)?
        (?:(?P<sec>\d+(?:[.,]\d+)?)\s*(?:["″”“]|''|′′|’’)\s*)?
        (?P<hem>[NSEWnsew])""",
    re.VERBOSE,
)
_DECIMAL = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$")


def _num(text):
    return float(text.replace(",", "."))


def parse_coordinates(text):
    """Parse a Google Maps coordinate string into (latitude, longitude).

    Accepts DMS (46°09'04.9"N 8°56'29.7"E) or decimal ("46.1569, 8.9416").
    Raises ValueError when the text is not a valid pair.
    """
    text = (text or "").strip()
    match = _DECIMAL.match(text)
    if match:
        lat, lon = _num(match.group(1)), _num(match.group(2))
    else:
        values = {}
        for m in _DMS.finditer(text):
            value = _num(m["deg"]) + _num(m["min"] or "0") / 60 + _num(m["sec"] or "0") / 3600
            hem = m["hem"].upper()
            if hem in "SW":
                value = -value
            axis = "lat" if hem in "NS" else "lon"
            if axis in values:
                raise ValueError("duplicate axis")
            values[axis] = value
        if len(values) != 2:
            raise ValueError("incomplete coordinates")
        lat, lon = values["lat"], values["lon"]
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("out of range")
    return round(lat, 6), round(lon, 6)


def format_coordinates(latitude, longitude):
    if latitude is None or longitude is None:
        return ""
    return f"{latitude}, {longitude}"
