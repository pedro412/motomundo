#!/usr/bin/env python3
"""
Test migration dependencies and fix any issues
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

def check_migration_dependencies():
    """Check if there are any migration dependency issues"""
    print("Checking migration dependencies...")
    
    try:
        # Try to create a migration executor
        executor = MigrationExecutor(connection)
        print("✅ Migration dependencies are valid")
        
        # Show migration plan
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            print(f"📋 Migrations to apply: {len(plan)}")
            for migration, backwards in plan:
                print(f"   {'↶' if backwards else '→'} {migration}")
        else:
            print("📋 No migrations to apply")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration dependency error: {e}")
        return False

def show_migration_status():
    """Show current migration status"""
    print("\nChecking migration status...")
    
    try:
        # Show migrations status
        from django.core.management.commands.showmigrations import Command
        command = Command()
        
        # Get migration status for clubs app
        from django.db.migrations.loader import MigrationLoader
        loader = MigrationLoader(connection)
        
        print("\nClubs app migrations:")
        clubs_migrations = loader.graph.nodes
        for node in clubs_migrations:
            if node[0] == 'clubs':
                applied = node in loader.applied_migrations
                status = "✅" if applied else "⏳"
                print(f"   {status} {node[1]}")
        
        print("\nGeography app migrations:")
        for node in clubs_migrations:
            if node[0] == 'geography':
                applied = node in loader.applied_migrations
                status = "✅" if applied else "⏳"
                print(f"   {status} {node[1]}")
        
    except Exception as e:
        print(f"❌ Error checking migration status: {e}")

if __name__ == "__main__":
    print("🔍 Migration Dependency Checker")
    print("=" * 40)
    
    success = check_migration_dependencies()
    show_migration_status()
    
    if success:
        print("\n🎉 Migration dependencies are fixed!")
        print("💡 You should now be able to run: python manage.py migrate")
    else:
        print("\n❌ Migration dependency issues remain")
    
    sys.exit(0 if success else 1)
