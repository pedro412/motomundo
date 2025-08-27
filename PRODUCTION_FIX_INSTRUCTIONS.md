# Production Fix Instructions: USA/Texas State Issue

## Problem
- Chapter creation fails with foreign key constraint error
- `state_new_id=33` references non-existent record in `clubs_state` table
- USA/Texas data exists in `geography_state` but not in legacy `clubs_state`

## Solution Steps

### Method 1: Using the Fix Script (Recommended)

1. **Upload the fix script to your production server**:
   ```bash
   scp fix_production_texas_issue.py your-server:/path/to/motomundo/
   ```

2. **SSH into your production server**:
   ```bash
   ssh your-production-server
   cd /path/to/motomundo
   ```

3. **Run the fix script**:
   ```bash
   # If using Docker in production:
   docker-compose exec web python fix_production_texas_issue.py
   
   # If running Django directly:
   python fix_production_texas_issue.py
   
   # If using virtual environment:
   source venv/bin/activate
   python fix_production_texas_issue.py
   ```

### Method 2: Direct Database Commands (Alternative)

If you prefer direct database access:

1. **Connect to your production database**:
   ```bash
   # PostgreSQL example
   psql -h your-db-host -U your-db-user -d your-db-name
   ```

2. **Run these SQL commands**:
   ```sql
   -- Add USA to clubs_country if not exists
   INSERT INTO clubs_country (id, name, code) 
   SELECT 2, 'USA', 'US' 
   WHERE NOT EXISTS (SELECT 1 FROM clubs_country WHERE name = 'USA');
   
   -- Add Texas to clubs_state if not exists  
   INSERT INTO clubs_state (id, name, code, country_id) 
   SELECT 33, 'Texas', 'TX', 2 
   WHERE NOT EXISTS (SELECT 1 FROM clubs_state WHERE name = 'Texas');
   
   -- Verify the fix
   SELECT 'clubs_country:' as table_name, id, name FROM clubs_country WHERE name = 'USA'
   UNION ALL
   SELECT 'clubs_state:', id, name FROM clubs_state WHERE name = 'Texas';
   ```

### Method 3: Django Management Command

1. **Create the management command** (copy the file from `geography/management/commands/fix_usa_texas.py`)

2. **Run the command**:
   ```bash
   # In production
   python manage.py fix_usa_texas
   ```

## Verification

After running the fix, verify it works:

1. **Test chapter creation**:
   - Go to Django Admin
   - Try creating a chapter in Texas
   - Should work without foreign key errors

2. **Check database state**:
   ```sql
   SELECT COUNT(*) FROM clubs_country WHERE name = 'USA';  -- Should return 1
   SELECT COUNT(*) FROM clubs_state WHERE name = 'Texas';  -- Should return 1
   ```

## Important Notes

- **Backup first**: Always backup your production database before running fixes
- **Downtime**: The fix should take less than 1 minute with minimal downtime
- **Rollback**: If issues occur, you can remove the records:
  ```sql
  DELETE FROM clubs_state WHERE name = 'Texas';
  DELETE FROM clubs_country WHERE name = 'USA';
  ```

## Root Cause

This issue occurred because your application has two sets of geography tables:
- Legacy: `clubs_country` and `clubs_state` 
- New: `geography_country` and `geography_state`

The `Chapter` model still references the legacy tables via foreign keys, but new geography data was added to the new tables. The fix synchronizes both table sets.

## Long-term Solution

Consider migrating fully to the new geography tables and updating foreign key constraints in a future release to prevent this issue.
