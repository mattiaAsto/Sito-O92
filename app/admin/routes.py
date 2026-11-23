from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import inspect

from app.admin import admin_bp
from app.extensions import db


def admin_required(f):
    """Decorator to check if user is an admin."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    
    return decorated_function


@admin_bp.route("/", methods=["GET"])
@login_required
@admin_required
def dashboard():
    """Admin dashboard showing all table schemas."""
    tables = []
    
    # Get all models from the metadata
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    
    for table_name in sorted(table_names):
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)["constrained_columns"]
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        table_info = {
            "name": table_name,
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "row_count": db.session.execute(
                db.text(f"SELECT COUNT(*) FROM `{table_name}`")
            ).scalar(),
        }
        tables.append(table_info)
    
    return render_template("admin/dashboard.html", tables=tables)


@admin_bp.route("/table/<table_name>", methods=["GET"])
@login_required
@admin_required
def table_detail(table_name):
    """View detailed information about a specific table."""
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    
    if table_name not in table_names:
        return redirect(url_for("admin.dashboard"))
    
    columns = inspector.get_columns(table_name)
    primary_keys = inspector.get_pk_constraint(table_name)["constrained_columns"]
    foreign_keys = inspector.get_foreign_keys(table_name)
    indexes = inspector.get_indexes(table_name)
    
    # Get sample data (limit to 50 rows)
    result = db.session.execute(
        db.text(f"SELECT * FROM `{table_name}` LIMIT 50")
    )
    rows = [dict(row) for row in result.mappings()]
    
    table_info = {
        "name": table_name,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "row_count": db.session.execute(
            db.text(f"SELECT COUNT(*) FROM `{table_name}`")
        ).scalar(),
        "rows": rows,
    }
    
    return render_template("admin/table_detail.html", table=table_info)
