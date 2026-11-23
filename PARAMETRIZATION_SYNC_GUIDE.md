# Parametrization Synchronization System

## Overview

This system provides intelligent synchronization of parametrization data:

- **DEV/TEST Environment**: Always loads fresh data from PARAMETRIZATION Python files at app startup
- **PRODUCTION Environment**: Only loads if `FILL_PARAM_TABLE=true` env variable is set
- **Updates existing records** rather than recreating them

## How It Works

### Development/Testing

Every time you start the Flask development server, parametrization data is automatically synced from the Python files:

```bash
$ python run.py
[INFO] Development mode: Reloading parametrization from Python files
[PARAM] Synced 9 activities
[PARAM] Synced 4 disciplines
[PARAM] Synced 10 committee members
... (more sync messages)
[PARAM] Parametrization sync completed successfully!
```

This ensures:
- ✅ Dev/test data is always fresh
- ✅ No manual database cleanup needed
- ✅ Easy testing of parametrization changes
- ✅ All changes in PARAMETRIZATION/*.py files appear immediately

### Production (Render)

In production, parametrization is only synced if explicitly enabled:

**To enable parametrization sync in production:**

1. Add environment variable to Render dashboard:
   ```
   FILL_PARAM_TABLE=true
   ```

2. When you deploy (push to main branch):
   - Build script checks for `FILL_PARAM_TABLE`
   - If true: syncs data from PARAMETRIZATION files
   - If false/unset: uses existing database data

**To disable parametrization sync:**

1. Remove/unset the `FILL_PARAM_TABLE` environment variable
2. Next deployment will not sync, preserving existing database data

## Environment Variables

### FILL_PARAM_TABLE

Controls whether to sync parametrization data from Python files in production.

```bash
# Enable syncing (production only)
FILL_PARAM_TABLE=true

# Or equivalent values:
FILL_PARAM_TABLE=1
FILL_PARAM_TABLE=yes

# Disable/unset (default)
# (not set)
FILL_PARAM_TABLE=false
```

### FLASK_ENV

Determines if running in development or production:

```bash
# Development (default if not set)
FLASK_ENV=development

# Production
FLASK_ENV=production
```

## Render.com Configuration

### build.sh

The `build.sh` script runs during Render's build phase:

1. Installs Python dependencies
2. Creates database tables
3. Runs Flask migrations
4. Checks FILL_PARAM_TABLE status
5. Reports deployment status

### Render.com Dashboard Setup

1. **Environment Variables**:
   ```
   FLASK_ENV=production
   DATABASE_URL=(your database URL)
   SECRET_KEY=(your secret key)
   FILL_PARAM_TABLE=true  (optional, only if you want to sync)
   ```

2. **Build Command**:
   ```bash
   chmod +x build.sh && ./build.sh
   ```

3. **Start Command**:
   ```bash
   gunicorn run:app
   ```

## Deployment Scenarios

### Scenario 1: Initial Production Deployment

```
1. Set environment variables in Render dashboard
2. Set FILL_PARAM_TABLE=true
3. Push code to main
4. Render runs build.sh
5. Parametrization data synced from PARAMETRIZATION/*.py
6. All 95+ items created in database
7. Website goes live with parametrization data
```

### Scenario 2: Update Parametrization Data

```
1. Admin edits data via /panel/parametrization/ web interface
2. Data updated in database
3. Website shows updated content immediately
4. No deployment needed
```

### Scenario 3: Redeploy with Updated Python Files

```
1. Update PARAMETRIZATION/*.py files locally
2. Test in dev (data auto-syncs)
3. Push to production
4. Set FILL_PARAM_TABLE=true in Render dashboard
5. Trigger new deployment
6. build.sh syncs updated data from Python files
7. Database updated with new parametrization
```

### Scenario 4: Preserve Database Data During Deploy

```
1. Admin has made changes via web interface
2. Developers push code updates
3. Leave FILL_PARAM_TABLE unset (or false)
4. Render deploys without touching parametrization data
5. Admin's changes preserved in database
```

## Implementation Details

### Synchronization Logic

The `initialize_parametrization()` function:

1. **Checks conditions**:
   - Is FLASK_ENV set to production?
   - If production: Is FILL_PARAM_TABLE true?
   - If dev/test: Always proceed

2. **Creates tables** if they don't exist

3. **For each parametrization category**:
   - Load data from PARAMETRIZATION Python file
   - For each item:
     - Find existing record by unique key
     - If exists: update fields
     - If not exists: create new record
   - Log progress

4. **Commits changes** to database

### Key Features

✅ **Idempotent** - Safe to run multiple times
✅ **Updates existing** - Doesn't recreate everything
✅ **Preserves order** - Maintains display order
✅ **Logs progress** - See what's being synced
✅ **Error handling** - Rolls back on errors
✅ **Dev/prod aware** - Different behavior per environment

### Unique Keys Used for Matching

Each model uses a sensible unique key to find existing records:

- Activity: `tab` (e.g., "Neve", "Estate")
- Discipline: `name`
- CommitteeMember: `name`
- OtherRole: `name`
- Monitor: `name`
- Contact: `role` + `name` combination
- Club: `label`
- Sponsor: `label`
- Setting: `key`
- ShopMaterial: `slug`
- CalendarCategory: `key`

## Console Output

### Dev/Test Mode

```
[INFO] Dev/Test mode: Reloading parametrization from Python files
[PARAM] Synced 9 activities
[PARAM] Synced 4 disciplines
[PARAM] Synced 10 committee members
[PARAM] Synced 5 other roles
[PARAM] Synced 26 monitors
[PARAM] Synced 8 contacts
[PARAM] Synced 7 clubs
[PARAM] Synced 4 sponsors
[PARAM] Synced 2 settings
[PARAM] Synced 5 shop materials with prices and sizes
[PARAM] Synced 6 calendar categories
[PARAM] Parametrization sync completed successfully!
```

### Production Mode (with FILL_PARAM_TABLE=true)

```
[INFO] Production mode: Syncing parametrization from Python files
[PARAM] Starting parametrization sync from Python files...
[PARAM] Synced 9 activities
... (same as dev)
[PARAM] Parametrization sync completed successfully!
```

### Production Mode (without FILL_PARAM_TABLE)

```
[INFO] Production mode: FILL_PARAM_TABLE not set, skipping parametrization sync
```

## Troubleshooting

### "Parametrization sync failed in production"

**Cause**: PARAMETRIZATION/*.py files missing or corrupted

**Solution**:
1. Check files exist in repository
2. Check for Python syntax errors
3. Run locally to test: `python run.py`

### "Admin changes disappeared after deploy"

**Cause**: FILL_PARAM_TABLE was true, overwriting database

**Solution**:
1. If this was unintended, unset FILL_PARAM_TABLE
2. Redeploy without FILL_PARAM_TABLE
3. Admin changes will be preserved for next deployment

### "PARAMETRIZATION data not loading in dev"

**Cause**: Python files not found or initialization not running

**Solution**:
1. Check PARAMETRIZATION/*.py files exist
2. Run app with: `python run.py`
3. Check console for `[PARAM]` messages
4. If not appearing, check app logs for errors

## Migration Workflow

### Initial Setup

```bash
# 1. Local development
python run.py  # Data auto-syncs from PARAMETRIZATION files

# 2. Test changes
# Edit PARAMETRIZATION/*.py files
# Restart server - data syncs automatically

# 3. Deploy to production
git push origin main
# Render sees FILL_PARAM_TABLE=true
# Runs build.sh
# Syncs parametrization data
# Website live with new data
```

### After Initial Deployment

```bash
# Option A: Edit via admin panel
# No deployment needed, changes live immediately

# Option B: Redeploy with Python file changes
# 1. Update PARAMETRIZATION/*.py
# 2. Push to main
# 3. Set FILL_PARAM_TABLE=true
# 4. Render deploys and syncs
```

## Code Changes

### app/__init__.py

Added initialization call:

```python
from app.parametrization.initialization import initialize_parametrization
initialize_parametrization(app)
```

### app/parametrization/initialization.py

New module with:
- `should_fill_parametrization_tables()` - Determines if syncing should happen
- `initialize_parametrization(app)` - Orchestrates the sync
- `_sync_parametrization_from_files(app)` - Performs the actual sync

## Summary

```
Environment          FILL_PARAM_TABLE    Behavior
─────────────────────────────────────────────────────
Development          (ignored)           Always sync from Python files
Testing              (ignored)           Always sync from Python files
Production           Unset/False         Use database as-is
Production           True/1/yes          Sync from Python files
```

**Result**: Maximum flexibility for both development and production deployments!
