"""
SPONSORS
========
Page: Links -> tab "Sponsor"  (rendered by app/main/routes.py -> links())

To add a sponsor:
  1. Copy the logo in  app/main/static/pictures/sponsors/
     (.png .jpg .jpeg .svg .webp .gif)
     NOTE: every logo in that folder is also shown automatically in the footer
     "I nostri sponsor" of every page, sorted by file name.
  2. Add a dictionary to SPONSORS below.
  3. Redeploy.
"""

SPONSORS = [
    {
        "label": "Banca Stato",                 # text on the card
        "href": "https://www.bancastato.ch",     # sponsor website
        "logo": "BCST.svg",                      # file in main/static/pictures/sponsors
    },
]
