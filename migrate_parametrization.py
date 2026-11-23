#!/usr/bin/env python
"""Script to create database tables and seed parametrization data."""

from app import create_app, db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully")
    
    # Run seed
    from app.parametrization.seed import seed_all
    try:
        seed_all()
        print("\nAll operations completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.session.rollback()
        raise
