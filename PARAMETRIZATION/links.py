"""
USEFUL LINKS
============
Page: Links -> tabs "Federazioni" and "Utili"  (app/main/routes.py -> links())

No file to upload: add a {"label", "href"} dictionary to the "items" list of the
right group below, then redeploy.
The groups map to the tabs in this order: first group -> "Federazioni",
second group -> "Utili". Do not remove or reorder the groups.
"""

LINK_GROUPS = [
    {
        "title": "Federazioni e associazioni",
        "items": [
            {"label": "ASTI - Associazione Sportiva Ticinese", "href": "https://www.asti-ticino.ch"},
            {"label": "Swiss Orienteering", "href": "https://www.solv.ch"},
            {"label": "IOF - Federazione Internazionale di CO", "href": "https://www.orienteering.org"},
            {"label": "FISO - Federazione Italiana di CO", "href": "https://www.fiso.it"},
        ],
    },
    {
        "title": "Links utili",
        "items": [
            {"label": "Iscrizioni online TMO e nazionali", "href": "https://ol-events.ch"},
            {"label": "Iscrizioni online internazionali", "href": "https://www.orienteeringonline.net"},
            {"label": "Classifiche live TMO", "href": "https://www.classifiche.asti-ticino.ch"},
            {"label": "Classifiche live gare nazionali", "href": "https://www.picotiming.ch"},
            {"label": "La più grande mappa di orienteering del mondo", "href": "https://www.o-map.ch"},
            {"label": "Sportident", "href": "https://www.sportident.com"},
            {"label": "Svizzera su carta di CO", "href": "https://www.mapant.ch"},
            {"label": "Analisi gare di CO svizzere (Olana)", "href": "https://www.ol.zimaa.ch"},
            {"label": "Informazioni internazionali sulla CO", "href": "https://www.worldofo.com"},
            {"label": "Selezione Ticino (SeleTI)", "href": "https://www.asti-ticino.ch/co/index.php?folder=sele&main=sele"},
            {"label": "Cool and Clean", "href": "https://www.coolandclean.ch"},
        ],
    },
]
