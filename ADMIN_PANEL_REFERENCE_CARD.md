# Admin Panel - Reference Card

## 🚀 Quick Access

```
URL: /panel/
Login Required: YES
Admin Required: YES
Access: Dropdown menu → "Admin Panel"
```

---

## 📊 Dashboard Page (`/panel/`)

Shows all database tables in a responsive grid

### What You'll See
- Table names with database icons
- Row count statistics
- Column count per table
- Primary key indicators
- Foreign key count
- Clickable cards linking to details

### Responsive Layout
- **Mobile**: 1 column
- **Tablet**: 2 columns
- **Desktop**: Auto-fit (3+ columns)

---

## 🔍 Table Detail Page (`/panel/table/<name>`)

Deep dive into a specific table's schema

### Sections Displayed

**1. Summary Stats**
- Total rows in table
- Number of columns
- Primary keys count
- Foreign keys count

**2. Table Structure**
- Column names
- Data types (color-coded)
- Nullable status (Y/N)
- Key information
- Default values

**3. Foreign Keys** (if any)
- Local columns
- Referenced table
- Referenced columns
- Delete action

**4. Indexes** (if any)
- Index names
- Included columns
- Unique status

**5. Sample Data**
- First 50 records
- All columns visible
- NULL values highlighted
- Long values truncated

---

## 🎨 Color Scheme

| Color | Usage | Hex |
|-------|-------|-----|
| Dark Blue-Gray | Headers, text | #2c3e50 |
| Bright Blue | Buttons, links | #3498db |
| Red | Accents, alerts | #e74c3c |
| Green | Success, yes | #27ae60 |
| Orange | Warning, caution | #f39c12 |
| Teal | Info, misc | #16a085 |

---

## 🏷️ Badge Types

| Badge | Meaning | Color |
|-------|---------|-------|
| **PK** | Primary Key | Blue |
| **FK** | Foreign Key | Green |
| Data Type | Column type | Yellow |
| Nullable | Can be NULL | Orange |
| Unique | Unique index | Blue |

---

## 📱 Responsive Design

### Mobile (< 576px)
- Single column layout
- Full-width cards
- Stacked tables
- Touch-friendly buttons

### Tablet (576px - 768px)
- Two-column grid
- Side-by-side cards
- Readable tables
- Proper spacing

### Desktop (> 768px)
- Auto-fit columns
- Multiple cards per row
- Full-width tables
- Optimal viewing

---

## 🔐 Security Features

| Layer | Method | Status |
|-------|--------|--------|
| Authentication | Flask-Login | ✅ Required |
| Authorization | @admin_required | ✅ Required |
| Data Access | Read-only | ✅ Safe |
| SQL Injection | SQLAlchemy ORM | ✅ Protected |
| Session | Secure cookies | ✅ Enabled |

---

## 🛠️ Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | Flask | 3.x |
| Database ORM | SQLAlchemy | 2.x |
| Authentication | Flask-Login | 0.x |
| Frontend | Jinja2 | 3.x |
| Styling | Bootstrap + CSS3 | 5.3 |

---

## 📂 File Locations

```
Backend Routes:         app/admin/routes.py
Blueprint Setup:        app/admin/__init__.py
Dashboard Template:     app/admin/templates/admin/dashboard.html
Detail Template:        app/admin/templates/admin/table_detail.html
Styling:                app/admin/static/css/admin.css
Configuration:          app/__init__.py (blueprint registration)
Navigation:             app/main/templates/main/base.html
```

---

## 🔗 Useful URLs

| Path | Purpose |
|------|---------|
| `/panel/` | Main dashboard |
| `/panel/table/Users` | Users table schema |
| `/panel/table/calendar_activities` | Activities table |
| `/panel/table/[name]` | Any table details |
| `/auth/login` | Login if not authenticated |

---

## 💡 Tips & Tricks

1. **Find Any Table** - Dashboard lists all tables alphabetically
2. **Check Data** - Sample data shows what's actually in the table
3. **Understand Schema** - Badges and colors tell you about columns
4. **See Relationships** - Foreign keys show table connections
5. **Quick Back** - Use back button to return to dashboard
6. **Mobile Friendly** - Works great on phones and tablets

---

## ⚠️ Limitations

- 🔒 Read-only access (no editing)
- 📊 Shows only 50 sample records
- 🚫 No data export from panel
- 🔍 No advanced search/filter
- 📈 No performance metrics yet

---

## ✅ Check This First

**Can't access admin panel?**
1. ✓ Logged in?
2. ✓ Admin user? (is_admin = True)
3. ✓ Click "altro" dropdown
4. ✓ See "Admin Panel" link?

**Tables not showing?**
1. ✓ Database connected?
2. ✓ Tables exist in DB?
3. ✓ Refresh page?

**Styling looks wrong?**
1. ✓ CSS file loading? (check browser)
2. ✓ Clear browser cache
3. ✓ Check browser console for errors

---

## 🎯 Common Tasks

### View All Tables
→ Go to `/panel/`

### See Specific Table Schema
→ Click table card or go to `/panel/table/TableName`

### View Sample Data
→ Scroll to bottom of table detail page

### Understand Relationships
→ Check "Foreign Keys" section on detail page

### View All Indexes
→ Check "Indexes" section on table detail

---

## 🔄 Workflow Example

1. **Start** → Click Admin Panel link
2. **Dashboard** → See all tables
3. **Explore** → Click on table of interest
4. **Inspect** → Review schema, keys, indexes
5. **Preview** → Check sample data
6. **Return** → Click back button
7. **Compare** → Check other tables
8. **Understand** → View relationships

---

## 📞 Quick Reference

| Task | How-To |
|------|--------|
| Access Panel | Dropdown → Admin Panel |
| View Tables | Dashboard at `/panel/` |
| View Details | Click table card |
| Go Back | Click back button |
| Check Keys | See colored badges |
| See Data | Scroll down on detail page |
| Understand Types | Hover over type badges |
| Check Mobile | Resize browser |

---

## 🎓 Learning Resources

📖 **New to Admin Panel?**
→ Read `ADMIN_PANEL_QUICKSTART.md`

🔧 **Want Technical Details?**
→ Read `ADMIN_PANEL_IMPLEMENTATION.md`

📚 **Need Complete Docs?**
→ Read `ADMIN_PANEL_README.md`

✅ **Verify All Features?**
→ Check `ADMIN_PANEL_CHECKLIST.md`

🗂️ **Find Right Doc?**
→ See `DOCUMENTATION_INDEX.md`

---

## 🚀 Summary

The Admin Panel provides a **complete database inspection tool** with:
- ✅ Full schema viewing
- ✅ Sample data preview
- ✅ Relationship mapping
- ✅ Professional UI
- ✅ Mobile support
- ✅ Strong security

**Access it now**: Log in → "altro" dropdown → "Admin Panel"

---

*Last Updated: November 23, 2026*
*Status: Production Ready ✅*
