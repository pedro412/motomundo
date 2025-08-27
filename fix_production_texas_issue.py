#!/usr/bin/env python3
"""
Production fix for USA/Texas state foreign key constraint issue.

This script fixes the database inconsistency where:
1. Chapter model references clubs_state table via foreign key
2. But USA/Texas data was added to geography_state table
3. Need to sync both tables to resolve foreign key violations

Run this script in production to fix the issue.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.db import connection, transaction
from geography.models import Country, State

def main():
    print("=== Production Fix: USA/Texas State Issue ===")
    
    with transaction.atomic():
        try:
            # Step 1: Ensure USA exists in both country tables
            print("Step 1: Fixing country tables...")
            
            # Check if USA exists in geography_country
            try:
                geo_usa = Country.objects.get(name="USA")
                print(f"✓ USA exists in geography_country (ID: {geo_usa.id})")
            except Country.DoesNotExist:
                geo_usa = Country.objects.create(name="USA", code="US")
                print(f"✓ Created USA in geography_country (ID: {geo_usa.id})")
            
            # Add USA to clubs_country if not exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM clubs_country WHERE name = 'USA'")
                clubs_usa = cursor.fetchone()
                
                if not clubs_usa:
                    cursor.execute(
                        "INSERT INTO clubs_country (id, name, code) VALUES (%s, 'USA', 'US')",
                        [geo_usa.id]
                    )
                    print(f"✓ Added USA to clubs_country (ID: {geo_usa.id})")
                else:
                    print(f"✓ USA already exists in clubs_country (ID: {clubs_usa[0]})")
            
            # Step 2: Ensure Texas exists in both state tables
            print("\nStep 2: Fixing state tables...")
            
            # Check if Texas exists in geography_state
            try:
                geo_texas = State.objects.get(name="Texas", country=geo_usa)
                print(f"✓ Texas exists in geography_state (ID: {geo_texas.id})")
            except State.DoesNotExist:
                geo_texas = State.objects.create(name="Texas", country=geo_usa, code="TX")
                print(f"✓ Created Texas in geography_state (ID: {geo_texas.id})")
            
            # Add Texas to clubs_state if not exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM clubs_state WHERE name = 'Texas'")
                clubs_texas = cursor.fetchone()
                
                if not clubs_texas:
                    cursor.execute(
                        "INSERT INTO clubs_state (id, name, code, country_id) VALUES (%s, 'Texas', 'TX', %s)",
                        [geo_texas.id, geo_usa.id]
                    )
                    print(f"✓ Added Texas to clubs_state (ID: {geo_texas.id})")
                else:
                    print(f"✓ Texas already exists in clubs_state (ID: {clubs_texas[0]})")
            
            # Step 3: Verify foreign key constraints work
            print("\nStep 3: Verifying fix...")
            
            with connection.cursor() as cursor:
                # Check if any chapters reference invalid state IDs
                cursor.execute("""
                    SELECT c.id, c.name, c.state_new_id, cl.name as club_name
                    FROM clubs_chapter c
                    JOIN clubs_club cl ON c.club_id = cl.id
                    LEFT JOIN clubs_state s ON c.state_new_id = s.id
                    WHERE c.state_new_id IS NOT NULL AND s.id IS NULL
                """)
                orphaned_chapters = cursor.fetchall()
                
                if orphaned_chapters:
                    print(f"⚠️  Found {len(orphaned_chapters)} chapters with invalid state references:")
                    for chapter_id, chapter_name, state_id, club_name in orphaned_chapters:
                        print(f"   - Chapter '{chapter_name}' references non-existent state ID: {state_id}")
                        
                        # Auto-fix Texas-related chapters
                        if any(keyword in chapter_name.lower() for keyword in ['texas', 'houston', 'dallas', 'austin', 'san antonio']):
                            cursor.execute(
                                "UPDATE clubs_chapter SET state_new_id = %s WHERE id = %s",
                                [geo_texas.id, chapter_id]
                            )
                            print(f"   ✓ Fixed: Assigned chapter '{chapter_name}' to Texas")
                else:
                    print("✓ No orphaned chapters found")
            
            print(f"\n=== Fix Complete ===")
            print(f"USA Country ID: {geo_usa.id}")
            print(f"Texas State ID: {geo_texas.id}")
            print("✓ Chapter creation in Texas should now work correctly")
            
        except Exception as e:
            print(f"✗ Error during fix: {e}")
            raise
    
    print("\n=== Production fix completed successfully ===")

if __name__ == "__main__":
    main()
