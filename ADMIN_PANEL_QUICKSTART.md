# 🚀 Admin Panel - Quick Start Guide

## Get Started in 30 Seconds

### 1. **Login**
   - Open the website and log in with your admin account
   - (Test account: `webmaster@o-92.ch` / `admin@o-92.ch`)

### 2. **Navigate to Admin Panel**
   - Click the "altro" (more) dropdown menu in the top-right
   - Select **"Admin Panel"** with the shield icon
   - You'll be taken to `/panel/`

### 3. **Explore Tables**
   - See all database tables in a grid layout
   - Each card shows:
     - Table name
     - Number of columns
     - Number of rows
     - Primary key info
     - Foreign key count

### 4. **View Table Details**
   - Click "Visualizza Dettagli" (View Details) on any table
   - See complete schema information:
     - All columns with types
     - Nullable status
     - Keys and indexes
     - Sample data (first 50 rows)

---

## 🎯 Key Features

✨ **Dashboard**
- Quick overview of all tables
- Row count statistics
- Responsive card layout
- Easy navigation to details

✨ **Table Details**
- Full schema inspection
- Column definitions
- Relationship mapping
- Database indexes
- Real data preview

✨ **Security**
- Admin-only access
- Login required
- Proper authorization
- Read-only access

✨ **Design**
- Modern interface
- Mobile-friendly
- Color-coded information
- Professional styling

---

## 📍 URLs

```
Main Dashboard:     /panel/
Table Details:      /panel/table/Users
                    /panel/table/calendar_activities
                    /panel/table/[any_table_name]
```

---

## 🔐 Who Can Access?

- ✅ Users with `is_admin = True`
- ❌ Regular users (redirected to home)
- ❌ Anonymous users (redirected to login)

---

## 💡 Pro Tips

1. **View All Tables** - Dashboard shows every table in the database
2. **Check Data** - Sample data section shows real records (limited to 50)
3. **Understand Schema** - Color-coded badges show:
   - 🔵 Primary Keys (blue)
   - 🟢 Foreign Keys (green)
   - 🟡 Data Types (yellow)
   - 🔴 Nullable (red = required)

4. **Back Button** - Every detail page has a back button to dashboard
5. **Mobile Friendly** - Works great on phones and tablets

---

## 🛠️ For Developers

### Add Admin Check in Templates
```jinja2
{% if current_user.is_admin %}
  <a href="{{ url_for('admin_panel.dashboard') }}">Admin Panel</a>
{% endif %}
```

### Protect Routes
```python
from app.admin.routes import admin_required

@app.route('/sensitive')
@login_required
@admin_required
def sensitive_route():
    return "Only admins see this"
```

### Create New Admin User (in Python)
```python
from app.models import User
from app.extensions import db

admin = User(
    first_name="Admin",
    last_name="User",
    email="admin@example.com",
    is_admin=True
)
admin.set_password("password123")
db.session.add(admin)
db.session.commit()
```

---

## 📚 Documentation

For more details, see:
- 📖 `ADMIN_PANEL_README.md` - Complete documentation
- 📋 `ADMIN_PANEL_SUMMARY.md` - Feature overview
- 🔧 `ADMIN_PANEL_IMPLEMENTATION.md` - Technical details
- ✅ `ADMIN_PANEL_CHECKLIST.md` - Full checklist

---

## ❓ FAQ

**Q: Can I edit/delete data from the admin panel?**
A: No, it's read-only for safety. Use the database directly for modifications.

**Q: Why can't I access the admin panel?**
A: Check if you're logged in and if your account has `is_admin = True`.

**Q: How many records are shown?**
A: First 50 records per table (to avoid performance issues).

**Q: Does it work with my database?**
A: Yes! As long as it's supported by SQLAlchemy.

**Q: Can I customize the styling?**
A: Yes, edit `/app/admin/static/css/admin.css`

---

## 🎨 Styling Reference

### Colors Used
- **Headers**: Dark blue-gray gradient
- **Cards**: White with blue borders
- **Badges**: Color-coded (blue, green, yellow, red, teal)
- **Tables**: Striped rows with hover effect

### Responsive Breakpoints
- **Mobile**: < 576px (single column)
- **Tablet**: 576px - 768px (2 columns)
- **Desktop**: > 768px (auto-fit)

---

## 🚨 Important Notes

⚠️ **Admin Panel is Read-Only**
- No data can be modified through the panel
- Perfect for inspecting and understanding your database

⚠️ **Limited Sample Data**
- Only first 50 records shown
- Use database tools for large exports

⚠️ **Admin Access Only**
- Requires `is_admin = True`
- Access is strictly controlled

---

## ✨ What You Can Do

✅ View all database tables
✅ Inspect table schema
✅ See column definitions
✅ View data types
✅ Check primary keys
✅ View foreign keys
✅ See indexes
✅ Preview sample data
✅ Understand relationships

---

**Enjoy exploring your database!** 🎉

Need help? Check the full documentation in the docs folder.
