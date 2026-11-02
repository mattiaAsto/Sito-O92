"""
CLUBS
=====
Page: Links -> tab "Società"  (rendered by app/main/routes.py -> links())

To add a club:
  1. Copy the logo in  app/main/static/pictures/other_clubs/
     (UNKNOWN.png can be used as a placeholder)
  2. Add a dictionary to CLUBS below.
  3. Redeploy.
"""

CLUBS = [
    {"label": "ASCO Lugano", "href": "https://www.asco-lugano.ch", "logo": "ASCO.png"},
    {"label": "CO AGET Lugano", "href": "https://www.coaget.ch", "logo": "CO AGET.png"},
    {"label": "CO UTOE Bellinzona", "href": "https://www.utoe.ch/co", "logo": "CO UTOE.png"},
    {"label": "GOLD Savosa", "href": "https://www.gold-savosa.ch", "logo": "GOLD.png"},
    {"label": "GOV Valmaggia", "href": "https://www.gov-valmaggia.ch", "logo": "GOV.png"},
    {"label": "SCOM Mendrisio", "href": "https://www.scom-mendrisio.ch", "logo": "SCOM.png"},
    {"label": "UNITAS Malcantone", "href": "https://sites.google.com/view/unitascaslano", "logo": "UNITAS.png"},
]
