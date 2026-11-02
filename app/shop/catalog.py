"""Official O-92 materials; the data lives in PARAMETRIZATION/shop_materials.py."""

from PARAMETRIZATION.shop_materials import (
    MATERIALS_CONTACT_EMAIL,
    MATERIALS_CONTACT_NAME,
    MATERIALS_PDF,
    OFFICIAL_MATERIALS,
)

MATERIALS_BY_SLUG = {item["slug"]: item for item in OFFICIAL_MATERIALS}

for _item in OFFICIAL_MATERIALS:
    _lowest = min(_item["prices"], key=lambda p: float(p[1].replace(".-", "")))
    _item["from_price"] = _lowest[1]
    _item["has_range"] = len(_item["prices"]) > 1
