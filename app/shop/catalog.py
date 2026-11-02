"""Official O-92 materials in stock, from static/pdf/materiale_o-92_0525.pdf."""

MATERIALS_PDF = "pdf/materiale_o-92_0525.pdf"
MATERIALS_CONTACT_NAME = "Roberta De Maria"
MATERIALS_CONTACT_EMAIL = "roberta.demaria@gmail.com"

# Image paths are relative to the shop blueprint's static folder.
OFFICIAL_MATERIALS = [
    {
        "slug": "pigiami",
        "name": "Pigiami",
        "note": "Venduti completi (maglia e pantaloni abbinati). Ricamo nome su richiesta: CHF 6.-",
        "prices": [("Adulti", "100.-"), ("Giovani < 18", "85.-"), ("Bambini", "70.-")],
        "sizes": [
            ("Donna", "S / M / L"),
            ("Uomo", "S / M / L / XL / XXL"),
            ("Bambino", "150 / 160"),
        ],
        "images": [
            "img/materiale/pigiama-maglia.jpg",
            "img/materiale/pigiama-pantaloni-fronte.jpg",
            "img/materiale/pigiama-pantaloni-retro.jpg",
        ],
    },
    {
        "slug": "training",
        "name": "Training",
        "note": "Venduti completi (maglia e pantaloni abbinati).",
        "prices": [("Adulti", "155.-"), ("Giovani < 18", "140.-"), ("Bambini", "120.-")],
        "sizes": [
            ("Donna", "XS / S / M / L / XL / XXL"),
            ("Uomo", "S / M / L / XXL"),
            ("Bambino", "140 / 160"),
        ],
        "images": [
            "img/materiale/training-giacca.jpg",
            "img/materiale/training-pantaloni.jpg",
        ],
    },
    {
        "slug": "maglia-bucata",
        "name": "Maglia «bucata»",
        "note": "Modello TRIMTEX Basic mesh O-shirt. Poche taglie ancora disponibili.",
        "prices": [("Adulti", "45.-"), ("Giovani < 20", "35.-")],
        "sizes": [("Donna", "S / M / L"), ("Uomo", "S / M / L")],
        "images": ["img/materiale/maglia-bucata.jpg"],
    },
    {
        "slug": "borse",
        "name": "Borse",
        "note": "Borse vecchie blu. Numeri disponibili: 156, 157, 158, 176, 179, 182, 183, 184, 187, 189, 193, 194, 195, 196, 197. Le borse arancioni sono al momento finite.",
        "prices": [("Borsa blu", "10.-")],
        "sizes": [],
        "images": [],
    },
    {
        "slug": "vari",
        "name": "Vari",
        "note": "Capi vintage: pezzi singoli da visionare su richiesta o in occasione delle svendite.",
        "prices": [("Tape, stecca da 5 rotoli", "42.50")],
        "sizes": [],
        "images": [],
    },
]

MATERIALS_BY_SLUG = {item["slug"]: item for item in OFFICIAL_MATERIALS}

for _item in OFFICIAL_MATERIALS:
    _lowest = min(_item["prices"], key=lambda p: float(p[1].replace(".-", "")))
    _item["from_price"] = _lowest[1]
    _item["has_range"] = len(_item["prices"]) > 1
