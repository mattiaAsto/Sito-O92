"""
PARAMETRIZATION
===============
Every module in this package is a data source used by the site at startup.
Edit the data, redeploy the service, and the pages are filled automatically.

  sponsors.py            sponsor cards in the links page (+ logo upload)
  clubs.py               Ticino clubs in the links page
  links.py               federations and useful links in the links page
  documents.py           PDF documents and the pages that list them
  activities.py          "Attività" tabs and "Gare" disciplines
  people.py              committee, roles, monitors, contact persons
  shop_materials.py      official O-92 materials in the shop
  calendar_categories.py calendar categories and colors
  settings.py            single values (e-mail recipients)

Blog, news, calendar events, albums, van bookings and shop products are managed
from the GUI / database and are NOT handled here.
"""
