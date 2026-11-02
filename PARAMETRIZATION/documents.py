"""
DOCUMENTS (PDF)
===============
To add a document:
  1. Copy the PDF in the folder matching its "folder" value (see FOLDERS).
  2. Add an entry to DOCUMENTS (unique key -> label, folder, file).
  3. Add the key to every page that must list it in PAGE_DOCUMENTS
     (the order of the list is the order shown on the page).
  4. Redeploy.

To replace a document with a new version (e.g. new year): upload the new PDF,
change "file" (and the year in "label") in DOCUMENTS, delete the old PDF.
The calendar PDF is also linked directly in app/calendar/templates/calendar/index.html.
"""

# folder -> (blueprint owning the static files, sub-path inside that static folder)
FOLDERS = {
    "contacts": ("main", "pdf/contacts/"),                    # app/main/static/pdf/contacts/
    "whats_orienteering": ("main", "pdf/whats_orienteering/"),  # app/main/static/pdf/whats_orienteering/
    "who_are_we": ("main", "pdf/who_are_we/"),                # app/main/static/pdf/who_are_we/
    "shop": ("shop", "pdf/"),                                 # app/shop/static/pdf/
    "calendar": ("calendar", "pdf/"),                         # app/calendar/static/pdf/
    "vans": ("vans", "pdf/"),                                 # app/vans/static/pdf/
}

DOCUMENTS = {
    "calendar_2026": {"label": "Calendario annuale 2026", "folder": "calendar", "file": "calendario_annuale_2026.pdf"},
    "newcomers_info": {"label": "Informazioni per i nuovi soci", "folder": "contacts", "file": "newcomers_info_2022.pdf"},
    "swiss_competencies": {"label": "Competenze orientistiche (Swiss Orienteering)", "folder": "whats_orienteering", "file": "swiss_orienteering_competencies_21.pdf"},
    "iof_descriptions": {"label": "Descrizione dei punti IOF", "folder": "whats_orienteering", "file": "iof_control_descriptions.pdf"},
    "ticks_flyer": {"label": "Informazioni sulle zecche in Ticino", "folder": "whats_orienteering", "file": "ticks_flyer_ti.pdf"},
    "forest_legend": {"label": "Legenda cartina bosco", "folder": "whats_orienteering", "file": "forest_map_legend.pdf"},
    "city_legend": {"label": "Legenda cartina città", "folder": "whats_orienteering", "file": "city_map_legend.pdf"},
    "abc": {"label": "ABC della O-92", "folder": "who_are_we", "file": "o92_abc.pdf"},
    "ethics": {"label": "Carta etica nello sport", "folder": "who_are_we", "file": "sports_code_of_ethics.pdf"},
    "sponsorship": {"label": "Padrinato 2026", "folder": "who_are_we", "file": "sponsorship_2026.pdf"},
    "regulations": {"label": "Regolamento", "folder": "who_are_we", "file": "regulations_2025.pdf"},
    "statutes": {"label": "Statuto", "folder": "who_are_we", "file": "statutes_20251017.pdf"},
    "materials_stock": {"label": "Materiale O-92 a magazzino", "folder": "shop", "file": "materiale_o-92_0525.pdf"},
    "van_terms": {"label": "Condizioni noleggio", "folder": "vans", "file": "van_rental_terms_2026.pdf"},
    "van_third_party": {"label": "Uso veicoli di terzi", "folder": "vans", "file": "third_party_vehicle_use.pdf"},
}

# page -> document keys, in display order
PAGE_DOCUMENTS = {
    "links": [
        "calendar_2026", "newcomers_info", "swiss_competencies", "iof_descriptions",
        "ticks_flyer", "forest_legend", "city_legend", "abc", "ethics", "sponsorship",
        "regulations", "statutes", "materials_stock",
    ],
    "about_us": ["statutes", "regulations", "ethics", "abc", "sponsorship"],
    "whats_orienteering_advanced": ["swiss_competencies", "iof_descriptions", "forest_legend", "city_legend"],
    "whats_orienteering_ticks": ["ticks_flyer"],
    "contact": ["newcomers_info"],
    "vans": ["van_terms", "van_third_party"],
}


def page_documents(page):
    """Documents of a page as dicts with label, blueprint and static filename.

    In templates: url_for(doc.blueprint ~ '.static', filename=doc.filename)
    """
    result = []
    for key in PAGE_DOCUMENTS[page]:
        document = DOCUMENTS[key]
        blueprint, prefix = FOLDERS[document["folder"]]
        result.append(
            {
                "label": document["label"],
                "blueprint": blueprint,
                "filename": prefix + document["file"],
            }
        )
    return result
