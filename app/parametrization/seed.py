"""
Seed script to migrate parametrization data from Python files to database.
Run this after creating tables: python -c "from app.parametrization.seed import seed_all; seed_all()"
"""

from app import create_app, db
from app.parametrization.models.activities import Activity, Discipline
from app.parametrization.models.people import CommitteeMember, OtherRole, Monitor, Contact
from app.parametrization.models.links import LinkGroup, Link, Club, Sponsor
from app.parametrization.models.documents import Document, DocumentMapping
from app.parametrization.models.settings import Setting
from app.parametrization.models.shop import ShopMaterial, ShopMaterialPrice, ShopMaterialSize
from app.parametrization.models.calendar import CalendarCategory


def seed_activities():
    """Migrate activities from PARAMETRIZATION/activities.py"""
    if Activity.query.first():
        print("Activities already exist, skipping...")
        return
    
    activities_data = [
        {
            "tab": "Neve",
            "title": "Fine settimana sulla neve",
            "description": "Discesa a tutta velocità, sci di fondo per scoprire il proprio equilibrio (o cadere con stile) oppure una tranquilla passeggiata con le ciaspole: qui c'è un modo per divertirsi sulla neve per tutti i gusti!",
            "caption": "Brigels-Campra, 2025",
            "image": "brigels_campra_2025.png",
            "order": 0,
        },
        {
            "tab": "Inizio stagione",
            "title": 'Campo "mini" di inizio stagione',
            "description": "Si parte con il piede giusto! Chi è alle prime armi viene preso per mano e accompagnato alla sua prima gara, mentre i veterani possono scaldare le gambe e le bussole. Il tutto in ottima compagnia!",
            "caption": "Tesserete, 2023",
            "image": "tesserete_2023.jpeg",
            "order": 1,
        },
        {
            "tab": "Pasquale",
            "title": "Campo Pasquale",
            "description": "Quattro giorni nel cuore della Svizzera interna per scoprire boschi diversi da quelli ticinesi. Ad accompagnarci: giochi e attività serali e un pomeriggio a sorpresa che non vi anticipiamo!",
            "caption": "Malters, 2022",
            "image": "malters_2022.jpeg",
            "order": 2,
        },
        {
            "tab": "Estate",
            "title": "Trasferta estiva",
            "description": "Italia, Slovenia, Svezia… il mondo è pieno di cartine nuove da leggere! Ogni anno una meta diversa per mettere alla prova il proprio fiuto orientistico in posti che non si dimenticano.",
            "caption": "5 giorni Dolomiti, 2025",
            "image": "dolomites_5_days_2025.jpg",
            "order": 3,
        },
        {
            "tab": "CCCO",
            "title": "Campo Cantonale (CCCO)",
            "description": "Qui si fa sul serio, ma ci si diverte ancora di più! Tutte le società ticinesi si ritrovano per 5 giorni di allenamenti, gare e tanto divertimento. Ad accogliervi c'è un team di monitori giovane, motivato e pronto a darvi il meglio. Non vediamo l'ora di vedervi!",
            "caption": "Brigels, 2017",
            "image": "brigels_2017.jpg",
            "order": 4,
        },
        {
            "tab": "Grigliata",
            "title": "Grigliata sociale",
            "description": "Il profumo del collo di maiale sulla griglia ti guida fino a noi… e tra una chiacchiera e l'altra, c'è anche tempo per una simpatica garetta!",
            "caption": "Bellinzona, 2025",
            "image": "bellinzona_2025.jpg",
            "order": 5,
        },
        {
            "tab": "Sociale",
            "title": "Trasferta sociale",
            "description": "Corsa, nuovi luoghi, compagnia… e tanto, tanto cibo! Qui la gara è solo una scusa, ma ci partecipiamo con la massima motivazione (e con la pancia già pronta).",
            "caption": "Cesena (IT), 2023",
            "image": "cesena_2023.jpeg",
            "order": 6,
        },
        {
            "tab": "Maxi",
            "title": "Uscita maxi",
            "description": "Coming soon… Tenete gli occhi aperti, la sorpresa è in arrivo!",
            "caption": "L'uscita maxi tornerà nel 2027, non vediamo l'ora di proporvela!",
            "image": None,
            "order": 7,
        },
        {
            "tab": "Natale",
            "title": "Cena natalizia",
            "description": "Come da tradizione, ci ritroviamo per rivivere i momenti più belli dell'anno, tirare le somme della stagione e ringraziare chi ci ha dato una mano. Non può mancare l'ambito premio Güzz (a chi l'ha combinata più grossa!) e, per finire, ciò che ci riesce meglio dopo una corsa: mangiare!",
            "caption": "Ascona-Monte Verità, 2025",
            "image": "ascona_monte_verita_2025.jpg",
            "order": 8,
        },
    ]
    
    for data in activities_data:
        activity = Activity(**data)
        db.session.add(activity)
    
    db.session.commit()
    print(f"[OK] Seeded {len(activities_data)} activities")


def seed_disciplines():
    """Migrate disciplines from PARAMETRIZATION/activities.py"""
    if Discipline.query.first():
        print("Disciplines already exist, skipping...")
        return
    
    disciplines_data = [
        {
            "name": "Lunga distanza (long)",
            "description": "la gara di resistenza, per chi ama le lunghe corse nel bosco",
            "order": 0,
        },
        {
            "name": "Media distanza (middle)",
            "description": "tecnica e precisione, con il cronometro che corre veloce",
            "order": 1,
        },
        {
            "name": "Corta distanza (sprint)",
            "description": "ritmo da urlo, di solito tra le vie dei paesi",
            "order": 2,
        },
        {
            "name": "Staffetta",
            "description": "si corre in squadra, perché insieme è più bello (e più emozionante!)",
            "order": 3,
        },
    ]
    
    for data in disciplines_data:
        discipline = Discipline(**data)
        db.session.add(discipline)
    
    db.session.commit()
    print(f"[OK] Seeded {len(disciplines_data)} disciplines")


def seed_committee():
    """Migrate committee members from PARAMETRIZATION/people.py"""
    if CommitteeMember.query.first():
        print("Committee members already exist, skipping...")
        return
    
    committee_data = [
        {"role": "Presidente", "name": "Reto Depedrini", "location": "Rivera", "order": 0},
        {"role": "Vicepresidente, padrinato", "name": "Carla Bolis", "location": "Camorino", "order": 1},
        {"role": "Coord. attività sportive, resp. furgoni e noleggi", "name": "Alain Astori", "location": "Cugnasco", "order": 2},
        {"role": "Controllo all. cartine e resp. archivio foto", "name": "Feliciano Pawlowski", "location": "Rivera", "order": 3},
        {"role": "Responsabile attività", "name": "Alessandro Bolis", "location": "Camorino", "order": 4},
        {"role": "Responsabile materiale", "name": "Roberta De Maria", "location": None, "order": 5},
        {"role": "Responsabile G+S", "name": "Tito Balestra", "location": None, "order": 6},
        {"role": "Membro", "name": "Marzio Bianchi", "location": None, "order": 7},
        {"role": "Membro giovane", "name": "Davide De Giorgi", "location": None, "order": 8},
        {"role": "Membro giovane", "name": "Marta Riso", "location": None, "order": 9},
    ]
    
    for data in committee_data:
        member = CommitteeMember(**data)
        db.session.add(member)
    
    db.session.commit()
    print(f"[OK] Seeded {len(committee_data)} committee members")


def seed_other_roles():
    """Migrate other roles from PARAMETRIZATION/people.py"""
    if OtherRole.query.first():
        print("Other roles already exist, skipping...")
        return
    
    roles_data = [
        {"role": "Responsabile finanze", "name": "Elio Derighetti", "location": "Arcegno", "order": 0},
        {"role": "Responsabile magazzino", "name": "Alessandro Pawlowski", "location": "Rivera", "order": 1},
        {"role": "Responsabile iscrizioni", "name": "Stefano Maddalena", "location": "Bironico", "order": 2},
        {"role": "Membro CTCO", "name": "Tiziano Boiani", "location": "Cadenazzo", "order": 3},
        {"role": "Responsabile sito internet", "name": "Mattia Astori", "location": "Cugnasco", "order": 4},
    ]
    
    for data in roles_data:
        role = OtherRole(**data)
        db.session.add(role)
    
    db.session.commit()
    print(f"[OK] Seeded {len(roles_data)} other roles")


def seed_monitors():
    """Migrate monitors from PARAMETRIZATION/people.py"""
    if Monitor.query.first():
        print("Monitors already exist, skipping...")
        return
    
    monitors_data = [
        "Alain Astori", "Mattia Astori", "Tito Balestra", "Marzio Bianchi",
        "Alessandro Bolis", "Carla Bolis", "Nicolas Borgeaud", "Arianna Cambianica",
        "Filippo Cantoreggi", "Sergio Cantoreggi", "Roberta De Maria", "Elia Depedrini",
        "Laura Depedrini", "Sara Fonti", "Aline Gaberell", "Florian Howald",
        "Alessandro Juorno", "Massimo Juorno", "Alice Maddalena", "Giulia Maddalena",
        "Stefano Maddalena", "Lisa Matasci", "Marta Riso", "Patrick Rossetti",
        "Sandy Rusconi", "Alina Vecsey",
    ]
    
    for name in monitors_data:
        monitor = Monitor(name=name)
        db.session.add(monitor)
    
    db.session.commit()
    print(f"[OK] Seeded {len(monitors_data)} monitors")


def seed_contacts():
    """Migrate contacts from PARAMETRIZATION/people.py"""
    if Contact.query.first():
        print("Contacts already exist, skipping...")
        return
    
    contacts_data = [
        {"role": "Responsabile attività", "name": "Alessandro Bolis", "email": "alessandro.bolis3@gmail.com", "phone": None, "order": 0},
        {"role": "Noleggio furgoni", "name": "Alain Astori", "email": None, "phone": None, "order": 1},
        {"role": "Ordinazione materiale", "name": "Roberta De Maria", "email": "roberta.demaria@gmail.com", "phone": None, "order": 2},
        {"role": "Info e password iscrizioni gare", "name": "Stefano Maddalena", "email": "stemadda@bluewin.ch", "phone": None, "order": 3},
        {"role": "Responsabile all. cartine", "name": "Alain Astori", "email": None, "phone": "079 337 42 65", "order": 4},
        {"role": "Membro CTCO", "name": "Tiziano Boiani", "email": None, "phone": None, "order": 5},
        {"role": "Responsabile finanze", "name": "Elio Derighetti", "email": "leliodivo@bluewin.ch", "phone": None, "order": 6},
        {"role": "Responsabile sito internet", "name": "Mattia Astori", "email": "webmaster@o-92.ch", "phone": None, "order": 7},
    ]
    
    for data in contacts_data:
        contact = Contact(**data)
        db.session.add(contact)
    
    db.session.commit()
    print(f"[OK] Seeded {len(contacts_data)} contacts")


def seed_links():
    """Migrate links from PARAMETRIZATION/links.py"""
    if LinkGroup.query.first():
        print("Link groups already exist, skipping...")
        return
    
    link_groups_data = [
        {
            "title": "Federazioni e associazioni",
            "order": 0,
            "items": [
                {"label": "Informazioni internazionali sulla CO", "href": "https://www.worldofo.com", "order": 0},
                {"label": "ASTI - Associazione Sportiva Ticinese", "href": "https://www.asti-ticino.ch", "order": 1},
                {"label": "Selezione Ticino (SeleTI)", "href": "https://www.asti-ticino.ch/SeleTI", "order": 2},
                {"label": "Swiss Orienteering", "href": "https://www.solv.ch", "order": 3},
                {"label": "FISO - Federazione Italiana di CO", "href": "https://www.fiso.it", "order": 4},
                {"label": "IOF - Federazione Internazionale di CO", "href": "https://www.orienteering.org", "order": 5},
                {"label": "Cool and Clean", "href": "https://www.coolandclean.ch", "order": 6},
            ],
        },
        {
            "title": "Links utili",
            "order": 1,
            "items": [
                {"label": "Iscrizioni online TMO e nazionali", "href": "https://ol-events.ch", "order": 0},
                {"label": "Iscrizioni online internazionali", "href": "https://www.orienteeringonline.net", "order": 1},
                {"label": "Classifiche live TMO", "href": "https://www.classifiche.asti-ticino.ch", "order": 2},
                {"label": "Classifiche live gare nazionali", "href": "https://www.picotiming.ch", "order": 3},
                {"label": "La più grande mappa di orienteering del mondo", "href": "https://www.o-map.ch", "order": 4},
                {"label": "SIAC Service", "href": "https://www.sportident.com", "order": 5},
                {"label": "Svizzera su carta di CO", "href": "https://www.mapant.ch", "order": 6},
                {"label": "Analisi gare di CO svizzere (Olana)", "href": "https://www.ol.zimaa.ch", "order": 7},
            ],
        },
    ]
    
    for group_data in link_groups_data:
        items_data = group_data.pop("items")
        group = LinkGroup(**group_data)
        db.session.add(group)
        db.session.flush()
        
        for item_data in items_data:
            link = Link(group_id=group.id, **item_data)
            db.session.add(link)
    
    db.session.commit()
    print(f"[OK] Seeded {len(link_groups_data)} link groups with links")


def seed_clubs():
    """Migrate clubs from PARAMETRIZATION/clubs.py"""
    if Club.query.first():
        print("Clubs already exist, skipping...")
        return
    
    clubs_data = [
        {"label": "ASCO Lugano", "href": "https://www.asco-lugano.ch", "logo": "ASCO.png", "order": 0},
        {"label": "CO AGET Lugano", "href": "https://www.coaget.ch", "logo": "CO AGET.png", "order": 1},
        {"label": "CO UTOE Bellinzona", "href": "https://utoe.ch/?page_id=1890", "logo": "CO UTOE.png", "order": 2},
        {"label": "GOLD Savosa", "href": "https://www.gold-savosa.ch", "logo": "GOLD.png", "order": 3},
        {"label": "GOV Valmaggia", "href": "https://www.gov-vallemaggia.ch", "logo": "GOV.png", "order": 4},
        {"label": "SCOM Mendrisio", "href": "https://www.scom-mendrisio.ch", "logo": "SCOM.png", "order": 5},
        {"label": "UNITAS Malcantone", "href": "https://sites.google.com/view/unitascaslano", "logo": "UNITAS.png", "order": 6},
    ]
    
    for data in clubs_data:
        club = Club(**data)
        db.session.add(club)
    
    db.session.commit()
    print(f"[OK] Seeded {len(clubs_data)} clubs")


def seed_sponsors():
    """Migrate sponsors from PARAMETRIZATION/sponsors.py"""
    if Sponsor.query.first():
        print("Sponsors already exist, skipping...")
        return
    
    sponsors_data = [
        {"label": "Banca Stato", "href": "https://www.bancastato.ch", "logo": "BCST.svg", "order": 0},
        {"label": "Comune di Monteceneri", "href": "https://www.monteceneri.ch/", "logo": "monteceneri.svg", "order": 1},
        {"label": "Comune di Cugnasco-Gerra", "href": "https://www.cugnasco-gerra.ch/", "logo": "cugnasco.svg", "order": 2},
        {"label": "Comune di Gambarogno", "href": "https://www.gambarogno.ch/", "logo": "gambarogno.svg", "order": 3},
    ]
    
    for data in sponsors_data:
        sponsor = Sponsor(**data)
        db.session.add(sponsor)
    
    db.session.commit()
    print(f"[OK] Seeded {len(sponsors_data)} sponsors")


def seed_settings():
    """Migrate settings from PARAMETRIZATION/settings.py"""
    if Setting.query.first():
        print("Settings already exist, skipping...")
        return
    
    settings_data = [
        {
            "key": "CONTACT_EMAIL",
            "value": "info@o-92.ch",
            "description": "Recipient of the contacts form",
            "value_type": "email",
        },
        {
            "key": "VANS_EMAIL",
            "value": "furgoni@o-92.ch",
            "description": "Recipient of van rental requests",
            "value_type": "email",
        },
    ]
    
    for data in settings_data:
        setting = Setting(**data)
        db.session.add(setting)
    
    db.session.commit()
    print(f"[OK] Seeded {len(settings_data)} settings")


def seed_shop_materials():
    """Migrate shop materials from PARAMETRIZATION/shop_materials.py"""
    if ShopMaterial.query.first():
        print("Shop materials already exist, skipping...")
        return
    
    materials_data = [
        {
            "slug": "pigiami",
            "name": "Pigiami",
            "note": "Venduti completi (maglia e pantaloni abbinati). Ricamo nome su richiesta: CHF 6.-",
            "order": 0,
            "prices": [
                {"label": "Adulti", "price": "100.-", "order": 0},
                {"label": "Giovani < 18", "price": "85.-", "order": 1},
                {"label": "Bambini", "price": "70.-", "order": 2},
            ],
            "sizes": [
                {"group": "Donna", "sizes": "S / M / L", "order": 0},
                {"group": "Uomo", "sizes": "S / M / L / XL / XXL", "order": 1},
                {"group": "Bambino", "sizes": "150 / 160", "order": 2},
            ],
        },
        {
            "slug": "training",
            "name": "Training",
            "note": "Venduti completi (maglia e pantaloni abbinati).",
            "order": 1,
            "prices": [
                {"label": "Adulti", "price": "155.-", "order": 0},
                {"label": "Giovani < 18", "price": "140.-", "order": 1},
                {"label": "Bambini", "price": "120.-", "order": 2},
            ],
            "sizes": [
                {"group": "Donna", "sizes": "XS / S / M / L / XL / XXL", "order": 0},
                {"group": "Uomo", "sizes": "S / M / L / XXL", "order": 1},
                {"group": "Bambino", "sizes": "140 / 160", "order": 2},
            ],
        },
        {
            "slug": "maglia-bucata",
            "name": "Maglia «bucata»",
            "note": "Modello TRIMTEX Basic mesh O-shirt. Poche taglie ancora disponibili.",
            "order": 2,
            "prices": [
                {"label": "Adulti", "price": "45.-", "order": 0},
                {"label": "Giovani < 20", "price": "35.-", "order": 1},
            ],
            "sizes": [
                {"group": "Donna", "sizes": "S / M / L", "order": 0},
                {"group": "Uomo", "sizes": "S / M / L", "order": 1},
            ],
        },
        {
            "slug": "borse",
            "name": "Borse",
            "note": "Borse vecchie blu. Numeri disponibili: 156, 157, 158, 176, 179, 182, 183, 184, 187, 189, 193, 194, 195, 196, 197. Le borse arancioni sono al momento finite.",
            "order": 3,
            "prices": [
                {"label": "Borsa blu", "price": "10.-", "order": 0},
            ],
            "sizes": [],
        },
        {
            "slug": "vari",
            "name": "Vari",
            "note": "Capi vintage: pezzi singoli da visionare su richiesta o in occasione delle svendite.",
            "order": 4,
            "prices": [
                {"label": "Tape, stecca da 5 rotoli", "price": "42.50", "order": 0},
            ],
            "sizes": [],
        },
    ]
    
    for material_data in materials_data:
        prices_data = material_data.pop("prices")
        sizes_data = material_data.pop("sizes")
        
        material = ShopMaterial(**material_data)
        db.session.add(material)
        db.session.flush()
        
        for price_data in prices_data:
            price = ShopMaterialPrice(material_id=material.id, **price_data)
            db.session.add(price)
        
        for size_data in sizes_data:
            size = ShopMaterialSize(material_id=material.id, **size_data)
            db.session.add(size)
    
    db.session.commit()
    print(f"[OK] Seeded {len(materials_data)} shop materials with prices and sizes")


def seed_calendar_categories():
    """Migrate calendar categories from PARAMETRIZATION/calendar_categories.py"""
    if CalendarCategory.query.first():
        print("Calendar categories already exist, skipping...")
        return
    
    categories_data = [
        {"key": "training_wednesday", "activity_type": "allenamento", "label": "Allenamento - Mercoledì", "color": "#3E9E6B"},
        {"key": "training_friday", "activity_type": "allenamento", "label": "Allenamento - Venerdì", "color": "#A9D18E"},
        {"key": "race_ticino", "activity_type": "gara", "label": "Gara - Ticino", "color": "#64B5F6"},
        {"key": "race_switzerland", "activity_type": "gara", "label": "Gara - Svizzera", "color": "#4F86C6"},
        {"key": "other_activity", "activity_type": "attivita", "label": "Altre attività", "color": "#B39DDB"},
        {"key": "camp", "activity_type": "attivita", "label": "Campi", "color": "#A569BD"},
    ]
    
    for data in categories_data:
        category = CalendarCategory(**data)
        db.session.add(category)
    
    db.session.commit()
    print(f"[OK] Seeded {len(categories_data)} calendar categories")


def seed_all():
    """Run all seed functions."""
    print("\n[*] Starting parametrization data migration...")
    
    try:
        seed_activities()
        seed_disciplines()
        seed_committee()
        seed_other_roles()
        seed_monitors()
        seed_contacts()
        seed_links()
        seed_clubs()
        seed_sponsors()
        seed_settings()
        seed_shop_materials()
        seed_calendar_categories()
        
        print("\n[SUCCESS] All parametrization data migrated successfully!")
    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        db.session.rollback()
        raise


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_all()
