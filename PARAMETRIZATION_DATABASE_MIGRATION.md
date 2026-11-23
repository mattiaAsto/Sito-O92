"""
PARAMETRIZATION SYSTEM - DATABASE MIGRATION
=============================================

The O-92 website has been upgraded with a comprehensive parametrization system that moves
all configuration data from Python files to the database, allowing admin users to modify
page content without code changes or redeployment.

## Overview

Previously, site parametrization data (activities, committee members, sponsors, etc.) was
stored in PARAMETRIZATION/*.py files, requiring manual code changes and redeployment to
update content.

Now, this data is stored in database tables and can be edited through the admin panel
interface, making content management fast and easy.

## Directory Structure

The parametrization module is organized in app/parametrization/:

app/parametrization/
├── __init__.py              # Module initialization, imports all models
├── models/                  # Database models
│   ├── __init__.py
│   ├── activities.py        # Activity and Discipline models
│   ├── people.py            # Committee, Monitors, Contacts
│   ├── links.py             # Sponsors, Clubs, LinkGroups
│   ├── documents.py         # Document and DocumentMapping models
│   ├── settings.py          # Global site settings
│   ├── shop.py              # Shop materials, prices, sizes
│   └── calendar.py          # Calendar event categories
├── forms.py                 # WTForms for admin editing
├── seed.py                  # Migration script: Python → Database
└── docs/                    # Documentation

## Database Models

### Activities & Disciplines
- **Activity** - Events and activities (Neve, Estate, CCCO, etc.)
- **Discipline** - Race types (long, middle, sprint, relay)

### People Management
- **CommitteeMember** - Committee members with roles and locations
- **OtherRole** - Additional organizational roles
- **Monitor** - Training monitors and instructors
- **Contact** - Contact persons with email/phone info

### Links & Organizations
- **LinkGroup** - Grouped links (Federazioni, Links utili)
- **Link** - Individual links within groups
- **Club** - External orienteering clubs
- **Sponsor** - Organization sponsors

### Configuration
- **Setting** - Global site-wide settings (emails, etc.)
- **Document** - PDF and document files
- **DocumentMapping** - Maps documents to pages
- **ShopMaterial** - Merchandise for sale
- **ShopMaterialPrice** - Price variants
- **ShopMaterialSize** - Size variants
- **CalendarCategory** - Event type categories with colors

## Usage

### For Admins: Editing via Admin Panel

1. **Access the admin panel**:
   - Log in to the website as an admin user
   - Click "Admin Panel" in the top-right dropdown menu
   - Navigate to "Parametrization"

2. **Browse parametrization categories**:
   - Activities & Events
   - Race Disciplines
   - Committee Members
   - Monitors
   - Contacts
   - Sponsors & Clubs
   - Settings
   - Calendar Categories

3. **Edit items**:
   - Click "View" on any category
   - Click "Edit" on an item to modify it
   - Or click "+ Create" to add new items
   - Delete items with the "Delete" button

4. **Changes take effect immediately**:
   - No redeployment needed
   - Changes appear on the website immediately

### For Developers: Initial Migration

The seed script migrates all existing parametrization data from Python files to the database.

```bash
# In the Flask shell:
python -c "from app.parametrization.seed import seed_all; seed_all()"

# Or programmatically:
from app import create_app
from app.parametrization.seed import seed_all

app = create_app()
with app.app_context():
    seed_all()
```

Output:
```
📦 Starting parametrization data migration...
✓ Seeded 9 activities
✓ Seeded 4 disciplines
✓ Seeded 10 committee members
✓ Seeded 5 other roles
✓ Seeded 26 monitors
✓ Seeded 8 contacts
✓ Seeded 2 link groups with links
✓ Seeded 7 clubs
✓ Seeded 4 sponsors
✓ Seeded 2 settings
✓ Seeded 5 shop materials with prices and sizes
✓ Seeded 6 calendar categories
✅ All parametrization data migrated successfully!
```

### For Developers: Accessing Data in Code

Instead of importing from PARAMETRIZATION files, query the database:

```python
# Before (old):
from PARAMETRIZATION.activities import ACTIVITIES, DISCIPLINES
for activity in ACTIVITIES:
    print(activity['title'])

# After (new):
from app.parametrization.models.activities import Activity, Discipline
activities = Activity.query.order_by(Activity.order).all()
for activity in activities:
    print(activity.title)
```

## Forms

All parametrization data can be edited through forms in `app/parametrization/forms.py`:

- **ActivityForm** - Edit activities
- **DisciplineForm** - Edit race disciplines
- **CommitteeMemberForm** - Edit committee members
- **MonitorForm** - Edit monitors
- **ContactForm** - Edit contact persons
- **LinkGroupForm** - Edit link groups
- **LinkForm** - Edit links
- **ClubForm** - Edit clubs
- **SponsorForm** - Edit sponsors
- **SettingForm** - Edit global settings
- **ShopMaterialForm** - Edit shop materials
- **CalendarCategoryForm** - Edit calendar categories

## Admin Panel Routes

All parametrization management is available under `/panel/parametrization/`:

```
/panel/parametrization/              - Main index with all categories
/panel/parametrization/activities    - List activities
/panel/parametrization/activities/new    - Create activity
/panel/parametrization/activities/<id>/edit    - Edit activity
/panel/parametrization/activities/<id>/delete  - Delete activity

/panel/parametrization/disciplines   - List disciplines
/panel/parametrization/disciplines/new
/panel/parametrization/disciplines/<id>/edit
/panel/parametrization/disciplines/<id>/delete

/panel/parametrization/committee     - List committee members
/panel/parametrization/committee/new
/panel/parametrization/committee/<id>/edit
/panel/parametrization/committee/<id>/delete

/panel/parametrization/monitors      - List monitors
/panel/parametrization/monitors/new
/panel/parametrization/monitors/<id>/edit
/panel/parametrization/monitors/<id>/delete

/panel/parametrization/contacts      - List contacts
/panel/parametrization/contacts/new
/panel/parametrization/contacts/<id>/edit
/panel/parametrization/contacts/<id>/delete

/panel/parametrization/sponsors      - List sponsors
/panel/parametrization/sponsors/new
/panel/parametrization/sponsors/<id>/edit
/panel/parametrization/sponsors/<id>/delete

/panel/parametrization/clubs         - List clubs
/panel/parametrization/clubs/new
/panel/parametrization/clubs/<id>/edit
/panel/parametrization/clubs/<id>/delete

/panel/parametrization/settings      - List settings
/panel/parametrization/settings/<id>/edit

/panel/parametrization/calendar-categories  - List calendar categories
/panel/parametrization/calendar-categories/<id>/edit
```

## Security

- All routes require admin authentication (is_admin=True)
- Forms include CSRF protection via Flask-WTF
- All input is validated before database insertion
- No direct SQL injection possible (using SQLAlchemy ORM)

## Templates Structure

Templates are organized by category in:
`app/admin/templates/admin/parametrization/`

```
parametrization/
├── index.html                    - Main parametrization dashboard
├── activities/
│   ├── list.html                 - Activities list
│   └── form.html                 - Activity create/edit form
├── disciplines/
│   ├── list.html
│   └── form.html
├── people/
│   ├── committee_list.html
│   ├── committee_form.html
│   ├── monitors_list.html
│   ├── monitor_form.html
│   ├── contacts_list.html
│   └── contact_form.html
├── links/
│   ├── sponsors_list.html
│   ├── sponsor_form.html
│   ├── clubs_list.html
│   └── club_form.html
├── settings_list.html
├── setting_form.html
├── calendar_categories_list.html
└── calendar_category_form.html
```

## Migration Path

1. **Initial Setup**: Run seed.py to migrate data from PARAMETRIZATION/*.py to database
2. **Old Files**: Keep PARAMETRIZATION/*.py files for reference or archive them
3. **Code Updates**: Update routes/templates to query database instead of importing files
4. **Full Migration**: Once all code paths use database, can safely remove PARAMETRIZATION files

## Example: Using Database in Templates

Before (from PARAMETRIZATION files):
```jinja2
{% for activity in ACTIVITIES %}
    <div class="activity-tab">{{ activity.title }}</div>
{% endfor %}
```

After (from database):
```jinja2
{% for activity in activities %}
    <div class="activity-tab">{{ activity.title }}</div>
{% endfor %}
```

Where `activities` is queried in the route:
```python
@main.route('/attivita')
def attivita():
    activities = Activity.query.order_by(Activity.order).all()
    return render_template('attivita.html', activities=activities)
```

## Benefits

✅ **No Code Changes Needed** - Update content via admin panel
✅ **No Redeployment** - Changes take effect immediately
✅ **Easy CRUD** - Create, read, update, delete via web interface
✅ **Organized Structure** - Hierarchical model structure matches site organization
✅ **Type-Safe** - SQLAlchemy models provide type safety
✅ **Auditable** - Database records can be backed up and tracked
✅ **Scalable** - Easily add new parametrization categories
✅ **User-Friendly** - Admin-only access with CSRF protection

## Notes

- All parametrization data includes timestamps (created_at, updated_at)
- Order fields allow custom sorting
- Relationships properly cascaded (e.g., deleting a LinkGroup deletes its Links)
- All nullable fields properly handled in forms with Optional validators
- Email fields validated with Email() validator
- URLs validated with URL() validator
