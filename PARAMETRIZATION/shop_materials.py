"""
SHOP - official O-92 materials in stock
=======================================
Used by app/shop/catalog.py and app/shop/routes.py.

To add an article:
  1. Copy the photos in  app/shop/static/img/materiale/
  2. Add a dictionary to OFFICIAL_MATERIALS (structure below).
     "from_price" and "has_range" are computed automatically.
  3. Redeploy.

If the stock PDF changes, upload the new file in app/shop/static/pdf/, then update
MATERIALS_PDF here and the "materials_stock" entry in documents.py.

Dictionary structure:
  slug    unique, used in the URL (/shop/materiale/<slug>)
  name    article name
  note    text shown on the article page
  prices  [(label, price)]  price format "NN.-" or "NN.50"
  sizes   [(group, "S / M / L")]  or []
  images  paths relative to app/shop/static, or []
"""

MATERIALS_PDF = "pdf/materiale_o-92_0525.pdf"
MATERIALS_CONTACT_NAME = "Roberta De Maria"
MATERIALS_CONTACT_EMAIL = "roberta.demaria@gmail.com"

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
            "img/materiale/pigiama-maglia-fronte.jpg",
            "img/materiale/pigiama-maglia-retro.jpg",
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
