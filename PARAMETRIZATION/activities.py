"""
ACTIVITIES AND RACE DISCIPLINES
===============================
Page "Attività" (app/main/routes.py -> attivita())
  To add an activity:
    1. Copy the photo in  app/main/static/pictures/activities/other_activities/
    2. Add a dictionary to ACTIVITIES (order = order of the tabs).
       "image": None shows an "In arrivo" placeholder instead of a photo.
    3. Redeploy.
  Upcoming events are NOT set here: they come from the calendar (admin GUI).

Page "Gare" (app/main/routes.py -> gare())
  Add a dictionary to DISCIPLINES. The maps are fixed files:
  app/main/static/pictures/activities/races/canton_ticino.png and switzerland.png
"""

ACTIVITIES = [
    {
        "tab": "Neve",
        "title": "Weekend sulla neve",
        "description": "Discesa a tutta velocità, sci di fondo per scoprire il proprio equilibrio (o cadere con stile) oppure una tranquilla passeggiata con le ciaspole: qui c’è un modo per divertirsi sulla neve per tutti i gusti!",
        "caption": "Brigels-Campra, 2025",
        "image": "brigels_campra_2025.png",
    },
    {
        "tab": "Inizio stagione",
        "title": "Weekend di inizio stagione",
        "description": "Si parte con il piede giusto! Chi è alle prime armi viene preso per mano e accompagnato alla sua prima gara, mentre i veterani possono scaldare le gambe e le bussole. Il tutto in ottima compagnia!",
        "caption": "Tesserete, 2023",
        "image": "tesserete_2023.jpeg",
    },
    {
        "tab": "Pasquale",
        "title": "Campo Pasquale",
        "description": "Quattro giorni nel cuore della Svizzera interna per scoprire boschi diversi da quelli ticinesi. Ad accompagnarci: giochi e attività serali e un pomeriggio a sorpresa che non vi anticipiamo!",
        "caption": "Malters, 2022",
        "image": "malters_2022.jpeg",
    },
    {
        "tab": "Estate",
        "title": "Trasferta estiva",
        "description": "Italia, Slovenia, Svezia… il mondo è pieno di cartine nuove da leggere! Ogni anno una meta diversa per mettere alla prova il proprio fiuto orientistico in posti che non si dimenticano.",
        "caption": "5 giorni Dolomiti, 2025",
        "image": "dolomites_5_days_2025.jpg",
    },
    {
        "tab": "CCCO",
        "title": "Campo Cantonale (CCCO)",
        "description": "Qui si fa sul serio, ma ci si diverte ancora di più! Tutte le società ticinesi si ritrovano per 5 giorni di allenamenti, gare e tanto divertimento. Ad accogliervi c’è un team di monitori giovane, motivato e pronto a darvi il meglio. Non vediamo l’ora di vedervi!",
        "caption": "Brigels, 2017",
        "image": "brigels_2017.jpg",
    },
    {
        "tab": "Grigliata",
        "title": "Grigliata sociale",
        "description": "Il profumo del collo di maiale sulla griglia ti guida fino a noi… e tra una chiacchiera e l’altra, c’è anche tempo per una simpatica garetta!",
        "caption": "Bellinzona, 2025",
        "image": "bellinzona_2025.jpg",
    },
    {
        "tab": "Sociale",
        "title": "Trasferta sociale",
        "description": "Corsa, nuovi luoghi, compagnia… e tanto, tanto cibo! Qui la gara è solo una scusa, ma ci partecipiamo con la massima motivazione (e con la pancia già pronta).",
        "caption": "Cesena (IT), 2023",
        "image": "cesena_2023.jpeg",
    },
    {
        "tab": "Maxi",
        "title": "Uscita maxi",
        "description": "Coming soon… Tenete gli occhi aperti, la sorpresa è in arrivo!",
        "caption": "L’uscita maxi tornerà nel 2027, non vediamo l’ora di proporvela!",
        "image": None,
    },
    {
        "tab": "Natale",
        "title": "Cena natalizia",
        "description": "Come da tradizione, ci ritroviamo per rivivere i momenti più belli dell’anno, tirare le somme della stagione e ringraziare chi ci ha dato una mano. Non può mancare l’ambito premio Güz (a chi l’ha combinata più grossa!) e, per finire, ciò che ci riesce meglio dopo una corsa: mangiare!",
        "caption": "Ascona-Monte Verità, 2025",
        "image": "ascona_monte_verita_2025.jpg",
    },
]

DISCIPLINES = [
    {"name": "Lunga distanza (long)", "description": "la gara di resistenza, per chi ama le lunghe corse nel bosco"},
    {"name": "Media distanza (middle)", "description": "tecnica e precisione, con il cronometro che corre veloce"},
    {"name": "Corta distanza (sprint)", "description": "ritmo da urlo, di solito tra le vie dei paesi"},
    {"name": "Staffetta", "description": "si corre in squadra, perché insieme è più bello (e più emozionante!)"},
]
