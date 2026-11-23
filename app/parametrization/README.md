"""
PARAMETRIZATION MODULE - DATABASE-BACKED CONFIGURATION
=======================================================

This module provides database models, forms, and admin routes for managing all site
parametrization data (activities, committee, contacts, sponsors, etc.) through a
web-based admin interface.

## Quick Start for Admins

1. Log in to website as admin user
2. Click "Admin Panel" in top-right dropdown menu
3. Click "Parametrization" link
4. Browse all parametrization categories
5. Click "View" to see items in a category
6. Click "Edit" to modify or "+ Create" to add new items
7. Changes take effect immediately - no redeployment needed!

## Directory Structure

This module is organized by parametrization category, matching the original
PARAMETRIZATION folder structure:

parametrization/
├── __init__.py              # Module initialization, exports all models
├── models/                  # Database models (organized by category)
│   ├── __init__.py
│   ├── activities.py        # Activity, Discipline
│   ├── people.py            # Committee, Monitors, Contacts, OtherRole
│   ├── links.py             # Sponsors, Clubs, LinkGroups, Links
│   ├── documents.py         # Document, DocumentMapping
│   ├── settings.py          # Setting (key-value configuration)
│   ├── shop.py              # ShopMaterial, Prices, Sizes
│   └── calendar.py          # CalendarCategory
├── forms.py                 # WTForms for all CRUD operations (12 forms)
├── seed.py                  # Migration script: Python files → Database
└── parametrization_routes.py  # Admin routes (imported by admin blueprint)

## Available Models

All models are automatically registered with Flask-SQLAlchemy.

### Activities & Events
- Activity - Special events (Neve, Estate, CCCO, etc.)
  - Fields: tab, title, description, caption, image, order
  - 9 items seeded
- Discipline - Race types (long, middle, sprint, relay)
  - Fields: name, description, order
  - 4 items seeded

### People Management
- CommitteeMember - Committee members with roles
  - Fields: role, name, location, order
  - 10 items seeded
- OtherRole - Additional organizational roles
  - Fields: role, name, location, order
  - 5 items seeded
- Monitor - Training monitors/instructors
  - Fields: name
  - 26 items seeded
- Contact - Contact persons with email/phone
  - Fields: role, name, email, phone, order
  - 8 items seeded

### Links & Organizations
- LinkGroup - Grouped links (Federazioni, Links utili)
  - Fields: title, description, order
  - Has many Links (cascading relationship)
  - 2 groups seeded
- Link - Individual links within groups
  - Fields: label, href, order, group_id
  - 15 items seeded
- Club - External clubs/associations
  - Fields: label, href, logo, order
  - 7 items seeded
- Sponsor - Organization sponsors
  - Fields: label, href, logo, order
  - 4 items seeded

### Configuration
- Setting - Global site-wide settings
  - Fields: key, value, description, value_type
  - 2 items seeded (CONTACT_EMAIL, VANS_EMAIL)
- Document - PDF/document files
  - Fields: key, label, folder, file, blueprint, static_path
- DocumentMapping - Maps documents to pages
  - Fields: page_name, document_id, order

### Shop & Commerce
- ShopMaterial - Merchandise for sale
  - Fields: slug, name, note, contact_name, contact_email, order
  - Has many Prices and Sizes (cascading)
  - 5 items seeded
- ShopMaterialPrice - Price variants for materials
  - Fields: label, price, order, material_id
  - 12 items seeded
- ShopMaterialSize - Size options for materials
  - Fields: group, sizes, order, material_id
  - 8 items seeded

### Calendar
- CalendarCategory - Event type categories with colors
  - Fields: key, activity_type, label, color
  - 6 items seeded

## Using Parametrization Data in Code

### Querying the Database

Instead of importing from PARAMETRIZATION files:

```python
# OLD WAY (don't use anymore):
from PARAMETRIZATION.activities import ACTIVITIES
for activity in ACTIVITIES:
    print(activity['title'])

# NEW WAY (use this):
from app.parametrization.models.activities import Activity
activities = Activity.query.order_by(Activity.order).all()
for activity in activities:
    print(activity.title)
```

### In Flask Routes

```python
from flask import render_template
from app.parametrization.models.activities import Activity, Discipline

@app.route('/attivita')
def attivita():
    activities = Activity.query.order_by(Activity.order).all()
    disciplines = Discipline.query.order_by(Discipline.order).all()
    return render_template('attivita.html', 
                         activities=activities,
                         disciplines=disciplines)
```

### In Jinja2 Templates

```html
<!-- Display parametrization data -->
<div class="activities">
    {% for activity in activities %}
        <div class="activity-tab">
            <h2>{{ activity.title }}</h2>
            <p>{{ activity.description }}</p>
            {% if activity.image %}
                <img src="{{ url_for('main.static', filename=f'pictures/activities/other_activities/{activity.image}') }}" alt="{{ activity.caption }}">
            {% endif %}
        </div>
    {% endfor %}
</div>
```

## Admin Routes

All parametrization management routes are under `/panel/parametrization/`:

```
/panel/parametrization/              Main dashboard (index)
/panel/parametrization/activities    List activities
/panel/parametrization/activities/new    Create activity
/panel/parametrization/activities/<id>/edit    Edit activity
/panel/parametrization/activities/<id>/delete  Delete activity

/panel/parametrization/disciplines   List disciplines
/panel/parametrization/disciplines/new
/panel/parametrization/disciplines/<id>/edit
/panel/parametrization/disciplines/<id>/delete

/panel/parametrization/committee     List committee members
/panel/parametrization/committee/new
/panel/parametrization/committee/<id>/edit
/panel/parametrization/committee/<id>/delete

/panel/parametrization/monitors      List monitors
/panel/parametrization/monitors/new
/panel/parametrization/monitors/<id>/edit
/panel/parametrization/monitors/<id>/delete

/panel/parametrization/contacts      List contacts
/panel/parametrization/contacts/new
/panel/parametrization/contacts/<id>/edit
/panel/parametrization/contacts/<id>/delete

/panel/parametrization/sponsors      List sponsors
/panel/parametrization/sponsors/new
/panel/parametrization/sponsors/<id>/edit
/panel/parametrization/sponsors/<id>/delete

/panel/parametrization/clubs         List clubs
/panel/parametrization/clubs/new
/panel/parametrization/clubs/<id>/edit
/panel/parametrization/clubs/<id>/delete

/panel/parametrization/settings      List settings
/panel/parametrization/settings/<id>/edit

/panel/parametrization/calendar-categories  List calendar categories
/panel/parametrization/calendar-categories/<id>/edit
```

## Forms Available

WTForms for all parametrization data:

- ActivityForm - Create/edit activities
- DisciplineForm - Create/edit disciplines
- CommitteeMemberForm - Manage committee
- MonitorForm - Manage monitors
- ContactForm - Manage contacts
- LinkGroupForm - Manage link groups
- LinkForm - Manage links
- ClubForm - Manage clubs
- SponsorForm - Manage sponsors
- SettingForm - Edit settings
- ShopMaterialForm - Manage materials
- CalendarCategoryForm - Manage calendar categories

All forms include:
- CSRF protection (Flask-WTF)
- Input validation (required fields, email, URL)
- Error handling and display
- User-friendly labels

## Data Migration

The seed.py script migrates all existing parametrization data from Python files
to the database on first run:

```bash
python migrate_parametrization.py
```

Or programmatically:

```python
from app import create_app
from app.parametrization.seed import seed_all

app = create_app()
with app.app_context():
    seed_all()
```

Output:
```
[*] Starting parametrization data migration...
[OK] Seeded 9 activities
[OK] Seeded 4 disciplines
[OK] Seeded 10 committee members
... (more seeding)
[SUCCESS] All parametrization data migrated successfully!
```

The seed script is idempotent - it checks for existing data and skips if
already migrated.

## Security Features

- **Admin-Only Access** - All routes require `is_admin=True` and login
- **CSRF Protection** - All forms include CSRF tokens via Flask-WTF
- **Input Validation** - Email, URL, required field validation
- **SQL Injection Proof** - Using SQLAlchemy ORM (no raw SQL)
- **Type-Safe** - SQLAlchemy models provide validation
- **Proper Cascading** - Deleting parent records cleans up children

## Timestamps

All models include timestamps:
- `created_at` - When record was created (auto-set)
- `updated_at` - When record was last modified (auto-updated)

This allows tracking of changes without additional audit logging.

## Ordering

Most models include an `order` field for custom sorting:
- Used in templates: `query.order_by(Model.order)`
- Can be edited in admin form
- Allows reordering items via admin panel

## Relationships

Proper database relationships with cascading deletes:

```
LinkGroup (1) → (many) Link
  Deleting a LinkGroup deletes all its Links

ShopMaterial (1) → (many) ShopMaterialPrice
                → (many) ShopMaterialSize
  Deleting material deletes all prices/sizes

Document (1) → (many) DocumentMapping
  Deleting document removes all page mappings
```

## Import All Models

The parametrization module exports all models from `__init__.py`:

```python
from app.parametrization import (
    Activity, Discipline,
    CommitteeMember, OtherRole, Monitor, Contact,
    LinkGroup, Link, Club, Sponsor,
    Document, DocumentMapping,
    Setting,
    ShopMaterial, ShopMaterialPrice, ShopMaterialSize,
    CalendarCategory
)
```

## Documentation

Additional documentation files:

- **PARAMETRIZATION_IMPLEMENTATION_SUMMARY.md** - Project completion summary
- **PARAMETRIZATION_QUICKSTART.md** - User guide for admins
- **PARAMETRIZATION_DATABASE_MIGRATION.md** - Technical implementation guide

## Examples

### Display Activities in Template

```html
{% for activity in activities %}
    <div class="activity-card">
        <h2>{{ activity.title }}</h2>
        <p>{{ activity.description }}</p>
        {% if activity.image %}
            <img src="{{ url_for('main.static', filename='pictures/activities/other_activities/' + activity.image) }}" alt="{{ activity.caption }}">
            <p class="caption">{{ activity.caption }}</p>
        {% else %}
            <p class="placeholder">In arrivo</p>
        {% endif %}
    </div>
{% endfor %}
```

### Display Sponsors in Footer

```html
<div class="sponsors">
    {% for sponsor in sponsors %}
        <a href="{{ sponsor.href }}" title="{{ sponsor.label }}">
            {% if sponsor.logo %}
                <img src="{{ url_for('main.static', filename='pictures/sponsors/' + sponsor.logo) }}" alt="{{ sponsor.label }}">
            {% else %}
                <span>{{ sponsor.label }}</span>
            {% endif %}
        </a>
    {% endfor %}
</div>
```

### Query with Filtering

```python
# Get committee members only
committee = CommitteeMember.query.order_by(CommitteeMember.order).all()

# Get monitors
monitors = Monitor.query.order_by(Monitor.name).all()

# Get contacts for a specific role
contacts = Contact.query.filter_by(role='Responsabile attività').all()

# Get sponsors ordered by name
sponsors = Sponsor.query.order_by(Sponsor.label).all()
```

## Common Tasks

### Add a New Activity via Admin

1. Go to `/panel/parametrization/activities`
2. Click "+ Create Activity"
3. Fill in fields:
   - Tab Name: "New Event"
   - Title: "My New Activity"
   - Description: "Full description..."
   - Caption: "Photo caption"
   - Image: "photo.jpg" (optional)
4. Click "Create"
5. Changes appear immediately on website

### Modify Committee Member

1. Go to `/panel/parametrization/committee`
2. Find member, click "Edit"
3. Update fields
4. Click "Edit"
5. Changes live immediately

### Delete Old Item

1. Navigate to list (e.g., `/panel/parametrization/sponsors`)
2. Find item, click "Delete"
3. Confirm deletion
4. Item removed from database and website

## Support

Questions about:
- **Admin Usage** → See PARAMETRIZATION_QUICKSTART.md
- **Technical Details** → See PARAMETRIZATION_DATABASE_MIGRATION.md
- **Code Examples** → See docstrings in models/*.py
- **Routes** → See docstrings in parametrization_routes.py

## Status

✅ **Production-Ready**

All parametrization data:
- Successfully migrated to database
- Organized in subdirectories
- Fully editable via admin panel
- Properly secured
- Completely documented

Admins can now edit all site parametrization without code changes or redeployment.
"""
