"""
CALENDAR CATEGORIES AND COLORS
==============================
Used by app/calendar/palette.py (calendar, admin forms, models, EXPORT.py).

To add a category add an entry to ACTIVITY_CATEGORIES:
  key            unique identifier (stored in the database: never rename an existing one)
  activity_type  "allenamento" | "gara" | "attivita" - decides which page
                 (Allenamenti, Gare, Attività) and home box list the events
  label          text shown to users
  color          hex color (keep color-palette.txt in sync)
Events themselves are created from the admin GUI, not here.
"""

BASE_COLOR = "#F9A825"

ACTIVITY_CATEGORIES = {
    "training_wednesday": {
        "activity_type": "allenamento",
        "label": "Allenamento - Mercoledì",
        "color": "#A9D18E",
    },
    "training_friday": {
        "activity_type": "allenamento",
        "label": "Allenamento - Venerdì",
        "color": "#3E9E6B",
    },
    "race_ticino": {
        "activity_type": "gara",
        "label": "Gara - Ticino",
        "color": "#64B5F6",
    },
    "race_switzerland": {
        "activity_type": "gara",
        "label": "Gara - Svizzera",
        "color": "#4F86C6",
    },
    "other_activity": {
        "activity_type": "attivita",
        "label": "Altre attività",
        "color": "#B39DDB",
    },
    "camp": {
        "activity_type": "attivita",
        "label": "Campi",
        "color": "#A569BD",
    },
}
