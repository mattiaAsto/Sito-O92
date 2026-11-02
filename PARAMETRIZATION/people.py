"""
PEOPLE
======
"Chi siamo" page (app/main/routes.py -> chi_siamo()): COMMITTEE, OTHER_ROLES, MONITORS
"Contatti" page  (app/main/routes.py -> contatti()):  CONTACTS

Add / edit / remove a dictionary (or a name) and redeploy.
"location", "email" and "phone" may be None.
E-mails are written with "(at)" instead of "@" to avoid spam bots.
If a person changes role, update both pages when the role appears in both.

Slideshow in "Chi siamo": copy the images (.png .jpg .jpeg .webp .gif, ~950x340 px)
in app/main/static/pictures/slideshow/ - they are picked up automatically, sorted by name.
"""

COMMITTEE = [
    {"role": "Presidente", "name": "Reto Depedrini", "location": "Rivera"},
    {"role": "Vicepresidente, padrinato", "name": "Carla Bolis", "location": "Camorino"},
    {"role": "Coord. attività sportive, resp. furgoni e noleggi", "name": "Alain Astori", "location": "Cugnasco"},
    {"role": "Controllo all. cartine e resp. archivio foto", "name": "Feliciano Pawlowski", "location": "Rivera"},
    {"role": "Responsabile attività", "name": "Alessandro Bolis", "location": "Camorino"},
    {"role": "Responsabile materiale", "name": "Roberta De Maria", "location": None},
    {"role": "Responsabile G+S", "name": "Tito Balestra", "location": None},
    {"role": "Membro", "name": "Marzio Bianchi", "location": None},
    {"role": "Membro giovane", "name": "Davide De Giorgi", "location": None},
    {"role": "Membro giovane", "name": "Marta Riso", "location": None},
]

OTHER_ROLES = [
    {"role": "Responsabile finanze", "name": "Elio Derighetti", "location": "Arcegno"},
    {"role": "Responsabile magazzino", "name": "Alessandro Pawlowski", "location": "Rivera"},
    {"role": "Responsabile iscrizioni", "name": "Stefano Maddalena", "location": "Bironico"},
    {"role": "Membro CTCO", "name": "Tiziano Boiani", "location": "Cadenazzo"},
    {"role": "Responsabile sito internet", "name": "Mattia Astori", "location": "Cugnasco"},
]

MONITORS = ["Alain Astori", "Alessandro Juorno", "Alina Vecsey", "Mattia Astori", "Giulia Maddalena"]

CONTACTS = [
    {"role": "Responsabile attività", "name": "Alessandro Bolis", "email": "alessandro.bolis3(at)gmail.com", "phone": None},
    {"role": "Noleggio furgoni", "name": "Alain Astori", "email": None, "phone": None},
    {"role": "Ordinazione materiale", "name": "Roberta De Maria", "email": "roberta.demaria(at)gmail.com", "phone": None},
    {"role": "Info e password iscrizioni gare", "name": "Stefano Maddalena", "email": "stemadda(at)bluewin.ch", "phone": None},
    {"role": "Responsabile all. cartine", "name": "Alain Astori", "email": None, "phone": "079 337 42 65"},
    {"role": "Membro CTCO", "name": "Tiziano Boiani", "email": None, "phone": None},
    {"role": "Responsabile finanze", "name": "Elio Derighetti", "email": "leliodivo(at)bluewin.ch", "phone": None},
    {"role": "Responsabile sito internet", "name": "Mattia Astori", "email": "webmaster(at)o-92.ch", "phone": None},
]
