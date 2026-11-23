"""
Flask-Admin setup and configuration.

Registers all models with customized views and organizes them into categories.
"""

from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for


class AdminSecuredModelView(ModelView):
    """Base ModelView with admin-only access control."""
    
    def is_accessible(self):
        """Check if user is admin."""
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect non-admins to home page."""
        return redirect(url_for('main.index'))


class ParametrizationModelView(AdminSecuredModelView):
    """Base view for parametrization tables with standard CRUD."""
    
    # Enable searching
    can_search = True
    
    # Enable pagination
    page_size = 20


# Import all models at module level to avoid issues with scoping
from app.models import User, BlogPost, BlogImage, CalendarActivity
from app.parametrization.models.activities import Activity, Discipline
from app.parametrization.models.people import CommitteeMember, OtherRole, Monitor, Contact
from app.parametrization.models.links import LinkGroup, Link, Club, Sponsor
from app.parametrization.models.settings import Setting
from app.parametrization.models.shop import ShopMaterial, ShopMaterialPrice, ShopMaterialSize
from app.parametrization.models.calendar import CalendarCategory
from app.parametrization.models.documents import Document, DocumentMapping


def setup_admin_views(flask_admin, db_session):
    """
    Register all model views with Flask-Admin.
    
    Args:
        flask_admin: Flask-Admin instance (must already be bound to app)
        db_session: SQLAlchemy session
    """
    
    # ============================================================================
    # PARAMETRIZATION SECTION - Organized under "Parametrization" category
    # ============================================================================
    
    # Activities & Disciplines
    flask_admin.add_view(ParametrizationModelView(Activity, db_session, name='Activities', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(Discipline, db_session, name='Disciplines', category='Parametrization'))
    
    # People Management
    flask_admin.add_view(ParametrizationModelView(CommitteeMember, db_session, name='Committee Members', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(OtherRole, db_session, name='Other Roles', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(Monitor, db_session, name='Monitors', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(Contact, db_session, name='Contacts', category='Parametrization'))
    
    # Links & Clubs & Sponsors
    flask_admin.add_view(ParametrizationModelView(LinkGroup, db_session, name='Link Groups', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(Link, db_session, name='Links', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(Club, db_session, name='Clubs', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(Sponsor, db_session, name='Sponsors', category='Parametrization'))
    
    # Settings
    flask_admin.add_view(ParametrizationModelView(Setting, db_session, name='Settings', category='Parametrization'))
    
    # Shop Materials
    flask_admin.add_view(ParametrizationModelView(ShopMaterial, db_session, name='Shop Materials', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(ShopMaterialPrice, db_session, name='Material Prices', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(ShopMaterialSize, db_session, name='Material Sizes', category='Parametrization'))
    
    # Calendar Categories
    flask_admin.add_view(ParametrizationModelView(CalendarCategory, db_session, name='Calendar Categories', category='Parametrization'))
    
    # Documents
    flask_admin.add_view(ParametrizationModelView(Document, db_session, name='Documents', category='Parametrization'))
    flask_admin.add_view(ParametrizationModelView(DocumentMapping, db_session, name='Document Mappings', category='Parametrization'))
    
    # ============================================================================
    # CONTENT SECTION - Main app data
    # ============================================================================
    
    flask_admin.add_view(AdminSecuredModelView(User, db_session, name='Users', category='Content', endpoint='admin_users'))
    flask_admin.add_view(AdminSecuredModelView(BlogPost, db_session, name='Blog Posts', category='Content'))
    flask_admin.add_view(AdminSecuredModelView(BlogImage, db_session, name='Blog Images', category='Content'))
    flask_admin.add_view(AdminSecuredModelView(CalendarActivity, db_session, name='Calendar Activities', category='Content'))



