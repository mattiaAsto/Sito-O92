"""
Parametrization initialization and synchronization.

This module handles:
- DEV/TEST: Always loads parametrization from Python files at startup
- PRODUCTION: Only loads if FILL_PARAM_TABLE env variable is True
"""

import os
from flask import current_app


def should_fill_parametrization_tables():
    """
    Determine if we should fill parametrization tables from Python files.
    
    Returns:
        bool: True if parametrization should be loaded/updated
    """
    # In development/testing, always load from Python files
    if os.getenv('FLASK_ENV', 'development') != 'production':
        return True
    
    # In production, only load if explicitly enabled via env variable
    return os.getenv('FILL_PARAM_TABLE', 'false').lower() in ('true', '1', 'yes')


def initialize_parametrization(app):
    """
    Initialize parametrization data from Python files if needed.
    
    This should be called after db.init_app() but before any routes are accessed.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        from app.extensions import db
        
        # Check if we should load parametrization data
        if not should_fill_parametrization_tables():
            if os.getenv('FLASK_ENV') == 'production':
                app.logger.info("[PARAM] Production mode: FILL_PARAM_TABLE not set, skipping parametrization sync")
            return
        
        try:
            # Only create tables if they don't exist
            db.create_all()
            
            if os.getenv('FLASK_ENV') != 'production':
                # Dev/Test: Always resync from Python files
                app.logger.info("[PARAM] Dev/Test mode: Reloading parametrization from Python files")
                _sync_parametrization_from_files(app)
            else:
                # Production: Sync only once during deployment
                app.logger.info("[PARAM] Production mode: Syncing parametrization from Python files")
                _sync_parametrization_from_files(app)
                
        except Exception as e:
            app.logger.error(f"[PARAM] Error during parametrization initialization: {e}")
            raise


def _sync_parametrization_from_files(app):
    """
    Synchronize parametrization tables from Python files.
    
    Updates existing records and creates new ones if needed.
    
    Args:
        app: Flask application instance
    """
    from app.extensions import db
    from app.parametrization.models.activities import Activity, Discipline
    from app.parametrization.models.people import CommitteeMember, OtherRole, Monitor, Contact
    from app.parametrization.models.links import LinkGroup, Link, Club, Sponsor
    from app.parametrization.models.settings import Setting
    from app.parametrization.models.shop import ShopMaterial, ShopMaterialPrice, ShopMaterialSize
    from app.parametrization.models.calendar import CalendarCategory
    
    # Import Python parametrization files
    from PARAMETRIZATION.activities import ACTIVITIES, DISCIPLINES
    from PARAMETRIZATION.people import COMMITTEE, OTHER_ROLES, MONITORS, CONTACTS
    from PARAMETRIZATION.links import LINK_GROUPS
    from PARAMETRIZATION.clubs import CLUBS
    from PARAMETRIZATION.sponsors import SPONSORS
    from PARAMETRIZATION.settings import CONTACT_EMAIL, VANS_EMAIL
    from PARAMETRIZATION.shop_materials import OFFICIAL_MATERIALS
    from PARAMETRIZATION.calendar_categories import ACTIVITY_CATEGORIES
    
    app.logger.info("[PARAM] Starting parametrization sync from Python files...")
    
    try:
        # Sync Activities
        for order, activity_data in enumerate(ACTIVITIES):
            activity = Activity.query.filter_by(tab=activity_data['tab']).first()
            if activity:
                # Update existing
                activity.title = activity_data['title']
                activity.description = activity_data['description']
                activity.caption = activity_data['caption']
                activity.image = activity_data.get('image')
                activity.order = order
            else:
                # Create new
                activity = Activity(
                    tab=activity_data['tab'],
                    title=activity_data['title'],
                    description=activity_data['description'],
                    caption=activity_data['caption'],
                    image=activity_data.get('image'),
                    order=order
                )
                db.session.add(activity)
        app.logger.info(f"[PARAM] Synced {len(ACTIVITIES)} activities")
        
        # Sync Disciplines
        for order, disc_data in enumerate(DISCIPLINES):
            discipline = Discipline.query.filter_by(name=disc_data['name']).first()
            if discipline:
                discipline.description = disc_data['description']
                discipline.order = order
            else:
                discipline = Discipline(
                    name=disc_data['name'],
                    description=disc_data['description'],
                    order=order
                )
                db.session.add(discipline)
        app.logger.info(f"[PARAM] Synced {len(DISCIPLINES)} disciplines")
        
        # Sync Committee
        for order, member_data in enumerate(COMMITTEE):
            member = CommitteeMember.query.filter_by(name=member_data['name']).first()
            if member:
                member.role = member_data['role']
                member.location = member_data.get('location')
                member.order = order
            else:
                member = CommitteeMember(
                    role=member_data['role'],
                    name=member_data['name'],
                    location=member_data.get('location'),
                    order=order
                )
                db.session.add(member)
        app.logger.info(f"[PARAM] Synced {len(COMMITTEE)} committee members")
        
        # Sync Other Roles
        for order, role_data in enumerate(OTHER_ROLES):
            role = OtherRole.query.filter_by(name=role_data['name']).first()
            if role:
                role.role = role_data['role']
                role.location = role_data.get('location')
                role.order = order
            else:
                role = OtherRole(
                    role=role_data['role'],
                    name=role_data['name'],
                    location=role_data.get('location'),
                    order=order
                )
                db.session.add(role)
        app.logger.info(f"[PARAM] Synced {len(OTHER_ROLES)} other roles")
        
        # Sync Monitors
        existing_monitors = {m.name for m in Monitor.query.all()}
        for name in MONITORS:
            if name not in existing_monitors:
                monitor = Monitor(name=name)
                db.session.add(monitor)
        # Remove monitors not in MONITORS list
        for monitor in Monitor.query.all():
            if monitor.name not in MONITORS:
                db.session.delete(monitor)
        app.logger.info(f"[PARAM] Synced {len(MONITORS)} monitors")
        
        # Sync Contacts
        for order, contact_data in enumerate(CONTACTS):
            # Use role + name as unique key
            contact = Contact.query.filter_by(
                role=contact_data['role'],
                name=contact_data['name']
            ).first()
            if contact:
                contact.email = contact_data.get('email')
                contact.phone = contact_data.get('phone')
                contact.order = order
            else:
                contact = Contact(
                    role=contact_data['role'],
                    name=contact_data['name'],
                    email=contact_data.get('email'),
                    phone=contact_data.get('phone'),
                    order=order
                )
                db.session.add(contact)
        app.logger.info(f"[PARAM] Synced {len(CONTACTS)} contacts")
        
        # Sync Clubs
        for order, club_data in enumerate(CLUBS):
            club = Club.query.filter_by(label=club_data['label']).first()
            if club:
                club.href = club_data['href']
                club.logo = club_data.get('logo')
                club.order = order
            else:
                club = Club(
                    label=club_data['label'],
                    href=club_data['href'],
                    logo=club_data.get('logo'),
                    order=order
                )
                db.session.add(club)
        app.logger.info(f"[PARAM] Synced {len(CLUBS)} clubs")
        
        # Sync Sponsors
        for order, sponsor_data in enumerate(SPONSORS):
            sponsor = Sponsor.query.filter_by(label=sponsor_data['label']).first()
            if sponsor:
                sponsor.href = sponsor_data['href']
                sponsor.logo = sponsor_data.get('logo')
                sponsor.order = order
            else:
                sponsor = Sponsor(
                    label=sponsor_data['label'],
                    href=sponsor_data['href'],
                    logo=sponsor_data.get('logo'),
                    order=order
                )
                db.session.add(sponsor)
        app.logger.info(f"[PARAM] Synced {len(SPONSORS)} sponsors")
        
        # Sync Settings
        settings_map = {
            'CONTACT_EMAIL': CONTACT_EMAIL,
            'VANS_EMAIL': VANS_EMAIL,
        }
        for key, value in settings_map.items():
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
                db.session.add(setting)
        app.logger.info(f"[PARAM] Synced {len(settings_map)} settings")
        
        # Sync Shop Materials
        for order, material_data in enumerate(OFFICIAL_MATERIALS):
            material = ShopMaterial.query.filter_by(slug=material_data['slug']).first()
            if material:
                material.name = material_data['name']
                material.note = material_data.get('note')
                material.order = order
            else:
                material = ShopMaterial(
                    slug=material_data['slug'],
                    name=material_data['name'],
                    note=material_data.get('note'),
                    order=order
                )
                db.session.add(material)
                db.session.flush()
            
            # Sync prices
            for price_order, price_data in enumerate(material_data.get('prices', [])):
                price = ShopMaterialPrice.query.filter_by(
                    material_id=material.id,
                    label=price_data[0]
                ).first()
                if price:
                    price.price = price_data[1]
                    price.order = price_order
                else:
                    price = ShopMaterialPrice(
                        material_id=material.id,
                        label=price_data[0],
                        price=price_data[1],
                        order=price_order
                    )
                    db.session.add(price)
            
            # Sync sizes
            for size_order, size_data in enumerate(material_data.get('sizes', [])):
                size = ShopMaterialSize.query.filter_by(
                    material_id=material.id,
                    group=size_data[0]
                ).first()
                if size:
                    size.sizes = size_data[1]
                    size.order = size_order
                else:
                    size = ShopMaterialSize(
                        material_id=material.id,
                        group=size_data[0],
                        sizes=size_data[1],
                        order=size_order
                    )
                    db.session.add(size)
        
        app.logger.info(f"[PARAM] Synced {len(OFFICIAL_MATERIALS)} shop materials with prices and sizes")
        
        # Sync Calendar Categories
        for category_key, category_data in ACTIVITY_CATEGORIES.items():
            category = CalendarCategory.query.filter_by(key=category_key).first()
            if category:
                category.activity_type = category_data['activity_type']
                category.label = category_data['label']
                category.color = category_data['color']
            else:
                category = CalendarCategory(
                    key=category_key,
                    activity_type=category_data['activity_type'],
                    label=category_data['label'],
                    color=category_data['color']
                )
                db.session.add(category)
        
        app.logger.info(f"[PARAM] Synced {len(ACTIVITY_CATEGORIES)} calendar categories")
        
        # Commit all changes
        db.session.commit()
        app.logger.info("[PARAM] Parametrization sync completed successfully!")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"[PARAM] Error syncing parametrization: {e}")
        raise
