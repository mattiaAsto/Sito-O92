# Admin Panel Documentation

## Overview

A complete admin panel has been created for managing all database tables and their data. The panel is accessible only to users with `is_admin = True` and is styled with a cohesive modern design.

## Access

### URL
- **Main Dashboard**: `/panel/`
- **Table Details**: `/panel/table/<table_name>`

### Navigation
The Admin Panel link appears in the lateral dropdown menu only for admin users:
- Navigate to the **"altro"** (more) dropdown menu at the top right
- Look for **"Admin Panel"** with a shield icon (only visible if you're logged in as an admin)

## Features

### Dashboard View (`/panel/`)
The main dashboard displays:

1. **Statistics Cards** - Quick overview of row counts for each table
2. **Table Grid** - Cards for each database table showing:
   - Table name with database icon
   - Number of columns
   - Number of rows
   - Primary keys badge
   - Foreign keys count badge
   - "Visualizza Dettagli" (View Details) link

### Table Detail View (`/panel/table/<table_name>`)
Detailed view of a specific table with:

1. **Summary Statistics**
   - Total rows
   - Number of columns
   - Primary keys count
   - Foreign keys count

2. **Table Structure Section**
   - Lists all columns with:
     - Column name
     - Data type (color-coded)
     - Nullable status (Yes/No)
     - Key information (Primary Key / Foreign Key)
     - Default values

3. **Foreign Keys Section** (if applicable)
   - Lists all relationships with:
     - Local column(s)
     - Referenced table
     - Referenced column(s)
     - Delete action (CASCADE, etc.)

4. **Indexes Section** (if applicable)
   - Lists all database indexes with:
     - Index name
     - Columns included
     - Uniqueness status

5. **Sample Data Section**
   - Shows first 50 records from the table
   - All columns visible with proper formatting
   - NULL values highlighted
   - Long values truncated with ellipsis

## Security

### Access Control
- **Authentication Required**: All admin panel routes require user to be logged in
- **Admin-Only Access**: Only users with `is_admin = True` can access the panel
- **Role-Based Navigation**: Admin Panel link only shows in dropdown for admin users

### Implementation
Two-layer protection:
1. Flask-Login `@login_required` decorator
2. Custom `@admin_required` decorator checking `current_user.is_admin`

Unauthorized access attempts redirect to the homepage (`/`).

## Styling

### Color Scheme
- **Primary**: `#2c3e50` (Dark blue-gray)
- **Secondary**: `#3498db` (Bright blue)
- **Accent**: `#e74c3c` (Red)
- **Success**: `#27ae60` (Green)
- **Warning**: `#f39c12` (Orange)
- **Info**: `#16a085` (Teal)

### Design Features
- **Modern Gradient Background**: Linear gradient from light blue to light gray
- **Card-Based Layout**: Each table displayed as an interactive card
- **Hover Effects**: Cards lift slightly on hover with enhanced shadow
- **Badge System**: Color-coded badges for different information types
- **Responsive Design**: Mobile-friendly layout with proper grid adaptation

### CSS File
- Location: `/app/admin/static/css/admin.css`
- Size: ~7KB
- Mobile breakpoints: 768px and 576px

## Technical Details

### Files Created
1. **Backend**
   - `/app/admin/__init__.py` - Blueprint initialization
   - `/app/admin/routes.py` - Route handlers and admin_required decorator

2. **Frontend**
   - `/app/admin/templates/admin/dashboard.html` - Main dashboard template
   - `/app/admin/templates/admin/table_detail.html` - Table detail template
   - `/app/admin/static/css/admin.css` - Styling and layouts

### Database Access
- Uses SQLAlchemy's Inspector to dynamically query database schema
- No hardcoded table names
- Automatically displays all tables currently in the database

### Template Inheritance
- Extends `main/base.html` for consistent site styling
- Reuses navigation, header, footer, and authentication context
- Integrates seamlessly with existing site design

## Routes

### Blueprint Name
`admin_panel`

### Available Routes
| Path | Method | Function | Description |
|------|--------|----------|-------------|
| `/panel/` | GET | `dashboard()` | Main admin dashboard |
| `/panel/table/<table_name>` | GET | `table_detail()` | Detailed view of a table |

## Usage Examples

### For Developers
```python
# Check admin status in templates
{% if current_user.is_admin %}
  <a href="{{ url_for('admin_panel.dashboard') }}">Admin Panel</a>
{% endif %}

# In Python code
from app.admin.routes import admin_required

@admin_required
def some_admin_function():
    # Only admins can access this
    pass
```

### For Site Administrators
1. Log in to the site as an admin user
2. Click "altro" dropdown in navigation
3. Click "Admin Panel"
4. Browse all database tables and their structure
5. Click on any table to see detailed schema and sample data

## Notes

- The admin panel is read-only - no edit/delete functionality is provided
- Sample data shows first 50 records to avoid performance issues
- Table names and column info are dynamically fetched from the database
- The panel works with any database backend supported by SQLAlchemy
- All pages include back navigation to easily return to the main dashboard

## Future Enhancements

Possible features for future versions:
- Edit/delete records directly from the panel
- SQL query builder
- Database backups and exports
- Performance statistics and slow queries
- User activity logging
- Advanced filters for sample data
- Table/column search functionality
