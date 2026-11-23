"""Admin routes for parametrization data management."""

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app.admin import admin_bp
from app.extensions import db
from app.parametrization.forms import (
    ActivityForm, DisciplineForm, CommitteeMemberForm, MonitorForm,
    ContactForm, LinkGroupForm, LinkForm, ClubForm, SponsorForm,
    SettingForm, ShopMaterialForm, CalendarCategoryForm
)
from app.parametrization.models.activities import Activity, Discipline
from app.parametrization.models.people import CommitteeMember, OtherRole, Monitor, Contact
from app.parametrization.models.links import LinkGroup, Link, Club, Sponsor
from app.parametrization.models.settings import Setting
from app.parametrization.models.shop import ShopMaterial
from app.parametrization.models.calendar import CalendarCategory


def admin_required(f):
    """Decorator to check if user is an admin."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# PARAMETRIZATION INDEX
# ============================================================================

@admin_bp.route("/parametrization/", methods=["GET"])
@login_required
@admin_required
def parametrization_index():
    """Index page for all parametrization data."""
    stats = {
        'activities': Activity.query.count(),
        'disciplines': Discipline.query.count(),
        'committee': CommitteeMember.query.count(),
        'monitors': Monitor.query.count(),
        'contacts': Contact.query.count(),
        'link_groups': LinkGroup.query.count(),
        'clubs': Club.query.count(),
        'sponsors': Sponsor.query.count(),
        'settings': Setting.query.count(),
        'shop_materials': ShopMaterial.query.count(),
        'calendar_categories': CalendarCategory.query.count(),
    }
    return render_template("admin/parametrization/index.html", stats=stats)


# ============================================================================
# ACTIVITIES
# ============================================================================

@admin_bp.route("/parametrization/activities", methods=["GET"])
@login_required
@admin_required
def activities_list():
    """List all activities."""
    activities = Activity.query.order_by(Activity.order).all()
    return render_template("admin/parametrization/activities/list.html", activities=activities)


@admin_bp.route("/parametrization/activities/new", methods=["GET", "POST"])
@login_required
@admin_required
def activity_create():
    """Create new activity."""
    form = ActivityForm()
    if form.validate_on_submit():
        activity = Activity(
            tab=form.tab.data,
            title=form.title.data,
            description=form.description.data,
            caption=form.caption.data,
            image=form.image.data or None,
            order=Activity.query.count()
        )
        db.session.add(activity)
        db.session.commit()
        flash(f"Activity '{activity.tab}' created successfully!", "success")
        return redirect(url_for("admin.activities_list"))
    return render_template("admin/parametrization/activities/form.html", form=form, action="Create")


@admin_bp.route("/parametrization/activities/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def activity_edit(id):
    """Edit activity."""
    activity = Activity.query.get_or_404(id)
    form = ActivityForm()
    if form.validate_on_submit():
        activity.tab = form.tab.data
        activity.title = form.title.data
        activity.description = form.description.data
        activity.caption = form.caption.data
        activity.image = form.image.data or None
        db.session.commit()
        flash(f"Activity '{activity.tab}' updated successfully!", "success")
        return redirect(url_for("admin.activities_list"))
    elif request.method == "GET":
        form.tab.data = activity.tab
        form.title.data = activity.title
        form.description.data = activity.description
        form.caption.data = activity.caption
        form.image.data = activity.image
    return render_template("admin/parametrization/activities/form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/activities/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def activity_delete(id):
    """Delete activity."""
    activity = Activity.query.get_or_404(id)
    tab_name = activity.tab
    db.session.delete(activity)
    db.session.commit()
    flash(f"Activity '{tab_name}' deleted successfully!", "success")
    return redirect(url_for("admin.activities_list"))


# ============================================================================
# DISCIPLINES
# ============================================================================

@admin_bp.route("/parametrization/disciplines", methods=["GET"])
@login_required
@admin_required
def disciplines_list():
    """List all disciplines."""
    disciplines = Discipline.query.order_by(Discipline.order).all()
    return render_template("admin/parametrization/disciplines/list.html", disciplines=disciplines)


@admin_bp.route("/parametrization/disciplines/new", methods=["GET", "POST"])
@login_required
@admin_required
def discipline_create():
    """Create new discipline."""
    form = DisciplineForm()
    if form.validate_on_submit():
        discipline = Discipline(
            name=form.name.data,
            description=form.description.data,
            order=Discipline.query.count()
        )
        db.session.add(discipline)
        db.session.commit()
        flash(f"Discipline '{discipline.name}' created successfully!", "success")
        return redirect(url_for("admin.disciplines_list"))
    return render_template("admin/parametrization/disciplines/form.html", form=form, action="Create")


@admin_bp.route("/parametrization/disciplines/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def discipline_edit(id):
    """Edit discipline."""
    discipline = Discipline.query.get_or_404(id)
    form = DisciplineForm()
    if form.validate_on_submit():
        discipline.name = form.name.data
        discipline.description = form.description.data
        db.session.commit()
        flash(f"Discipline '{discipline.name}' updated successfully!", "success")
        return redirect(url_for("admin.disciplines_list"))
    elif request.method == "GET":
        form.name.data = discipline.name
        form.description.data = discipline.description
    return render_template("admin/parametrization/disciplines/form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/disciplines/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def discipline_delete(id):
    """Delete discipline."""
    discipline = Discipline.query.get_or_404(id)
    name = discipline.name
    db.session.delete(discipline)
    db.session.commit()
    flash(f"Discipline '{name}' deleted successfully!", "success")
    return redirect(url_for("admin.disciplines_list"))


# ============================================================================
# COMMITTEE MEMBERS
# ============================================================================

@admin_bp.route("/parametrization/committee", methods=["GET"])
@login_required
@admin_required
def committee_list():
    """List all committee members."""
    members = CommitteeMember.query.order_by(CommitteeMember.order).all()
    return render_template("admin/parametrization/people/committee_list.html", members=members)


@admin_bp.route("/parametrization/committee/new", methods=["GET", "POST"])
@login_required
@admin_required
def committee_create():
    """Create new committee member."""
    form = CommitteeMemberForm()
    if form.validate_on_submit():
        member = CommitteeMember(
            role=form.role.data,
            name=form.name.data,
            location=form.location.data or None,
            order=CommitteeMember.query.count()
        )
        db.session.add(member)
        db.session.commit()
        flash(f"Committee member '{member.name}' created successfully!", "success")
        return redirect(url_for("admin.committee_list"))
    return render_template("admin/parametrization/people/committee_form.html", form=form, action="Create")


@admin_bp.route("/parametrization/committee/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def committee_edit(id):
    """Edit committee member."""
    member = CommitteeMember.query.get_or_404(id)
    form = CommitteeMemberForm()
    if form.validate_on_submit():
        member.role = form.role.data
        member.name = form.name.data
        member.location = form.location.data or None
        db.session.commit()
        flash(f"Committee member '{member.name}' updated successfully!", "success")
        return redirect(url_for("admin.committee_list"))
    elif request.method == "GET":
        form.role.data = member.role
        form.name.data = member.name
        form.location.data = member.location
    return render_template("admin/parametrization/people/committee_form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/committee/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def committee_delete(id):
    """Delete committee member."""
    member = CommitteeMember.query.get_or_404(id)
    name = member.name
    db.session.delete(member)
    db.session.commit()
    flash(f"Committee member '{name}' deleted successfully!", "success")
    return redirect(url_for("admin.committee_list"))


# ============================================================================
# MONITORS
# ============================================================================

@admin_bp.route("/parametrization/monitors", methods=["GET"])
@login_required
@admin_required
def monitors_list():
    """List all monitors."""
    monitors = Monitor.query.order_by(Monitor.name).all()
    return render_template("admin/parametrization/people/monitors_list.html", monitors=monitors)


@admin_bp.route("/parametrization/monitors/new", methods=["GET", "POST"])
@login_required
@admin_required
def monitor_create():
    """Create new monitor."""
    form = MonitorForm()
    if form.validate_on_submit():
        monitor = Monitor(name=form.name.data)
        db.session.add(monitor)
        db.session.commit()
        flash(f"Monitor '{monitor.name}' created successfully!", "success")
        return redirect(url_for("admin.monitors_list"))
    return render_template("admin/parametrization/people/monitor_form.html", form=form, action="Create")


@admin_bp.route("/parametrization/monitors/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def monitor_edit(id):
    """Edit monitor."""
    monitor = Monitor.query.get_or_404(id)
    form = MonitorForm()
    if form.validate_on_submit():
        monitor.name = form.name.data
        db.session.commit()
        flash(f"Monitor '{monitor.name}' updated successfully!", "success")
        return redirect(url_for("admin.monitors_list"))
    elif request.method == "GET":
        form.name.data = monitor.name
    return render_template("admin/parametrization/people/monitor_form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/monitors/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def monitor_delete(id):
    """Delete monitor."""
    monitor = Monitor.query.get_or_404(id)
    name = monitor.name
    db.session.delete(monitor)
    db.session.commit()
    flash(f"Monitor '{name}' deleted successfully!", "success")
    return redirect(url_for("admin.monitors_list"))


# ============================================================================
# CONTACTS
# ============================================================================

@admin_bp.route("/parametrization/contacts", methods=["GET"])
@login_required
@admin_required
def contacts_list():
    """List all contacts."""
    contacts = Contact.query.order_by(Contact.order).all()
    return render_template("admin/parametrization/people/contacts_list.html", contacts=contacts)


@admin_bp.route("/parametrization/contacts/new", methods=["GET", "POST"])
@login_required
@admin_required
def contact_create():
    """Create new contact."""
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            role=form.role.data,
            name=form.name.data,
            email=form.email.data or None,
            phone=form.phone.data or None,
            order=Contact.query.count()
        )
        db.session.add(contact)
        db.session.commit()
        flash(f"Contact '{contact.name}' created successfully!", "success")
        return redirect(url_for("admin.contacts_list"))
    return render_template("admin/parametrization/people/contact_form.html", form=form, action="Create")


@admin_bp.route("/parametrization/contacts/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def contact_edit(id):
    """Edit contact."""
    contact = Contact.query.get_or_404(id)
    form = ContactForm()
    if form.validate_on_submit():
        contact.role = form.role.data
        contact.name = form.name.data
        contact.email = form.email.data or None
        contact.phone = form.phone.data or None
        db.session.commit()
        flash(f"Contact '{contact.name}' updated successfully!", "success")
        return redirect(url_for("admin.contacts_list"))
    elif request.method == "GET":
        form.role.data = contact.role
        form.name.data = contact.name
        form.email.data = contact.email
        form.phone.data = contact.phone
    return render_template("admin/parametrization/people/contact_form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/contacts/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def contact_delete(id):
    """Delete contact."""
    contact = Contact.query.get_or_404(id)
    name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f"Contact '{name}' deleted successfully!", "success")
    return redirect(url_for("admin.contacts_list"))


# ============================================================================
# SPONSORS & CLUBS
# ============================================================================

@admin_bp.route("/parametrization/sponsors", methods=["GET"])
@login_required
@admin_required
def sponsors_list():
    """List all sponsors."""
    sponsors = Sponsor.query.order_by(Sponsor.order).all()
    return render_template("admin/parametrization/links/sponsors_list.html", sponsors=sponsors)


@admin_bp.route("/parametrization/sponsors/new", methods=["GET", "POST"])
@login_required
@admin_required
def sponsor_create():
    """Create new sponsor."""
    form = SponsorForm()
    if form.validate_on_submit():
        sponsor = Sponsor(
            label=form.label.data,
            href=form.href.data,
            logo=form.logo.data or None,
            order=Sponsor.query.count()
        )
        db.session.add(sponsor)
        db.session.commit()
        flash(f"Sponsor '{sponsor.label}' created successfully!", "success")
        return redirect(url_for("admin.sponsors_list"))
    return render_template("admin/parametrization/links/sponsor_form.html", form=form, action="Create")


@admin_bp.route("/parametrization/sponsors/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def sponsor_edit(id):
    """Edit sponsor."""
    sponsor = Sponsor.query.get_or_404(id)
    form = SponsorForm()
    if form.validate_on_submit():
        sponsor.label = form.label.data
        sponsor.href = form.href.data
        sponsor.logo = form.logo.data or None
        db.session.commit()
        flash(f"Sponsor '{sponsor.label}' updated successfully!", "success")
        return redirect(url_for("admin.sponsors_list"))
    elif request.method == "GET":
        form.label.data = sponsor.label
        form.href.data = sponsor.href
        form.logo.data = sponsor.logo
    return render_template("admin/parametrization/links/sponsor_form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/sponsors/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def sponsor_delete(id):
    """Delete sponsor."""
    sponsor = Sponsor.query.get_or_404(id)
    label = sponsor.label
    db.session.delete(sponsor)
    db.session.commit()
    flash(f"Sponsor '{label}' deleted successfully!", "success")
    return redirect(url_for("admin.sponsors_list"))


@admin_bp.route("/parametrization/clubs", methods=["GET"])
@login_required
@admin_required
def clubs_list():
    """List all clubs."""
    clubs = Club.query.order_by(Club.order).all()
    return render_template("admin/parametrization/links/clubs_list.html", clubs=clubs)


@admin_bp.route("/parametrization/clubs/new", methods=["GET", "POST"])
@login_required
@admin_required
def club_create():
    """Create new club."""
    form = ClubForm()
    if form.validate_on_submit():
        club = Club(
            label=form.label.data,
            href=form.href.data,
            logo=form.logo.data or None,
            order=Club.query.count()
        )
        db.session.add(club)
        db.session.commit()
        flash(f"Club '{club.label}' created successfully!", "success")
        return redirect(url_for("admin.clubs_list"))
    return render_template("admin/parametrization/links/club_form.html", form=form, action="Create")


@admin_bp.route("/parametrization/clubs/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def club_edit(id):
    """Edit club."""
    club = Club.query.get_or_404(id)
    form = ClubForm()
    if form.validate_on_submit():
        club.label = form.label.data
        club.href = form.href.data
        club.logo = form.logo.data or None
        db.session.commit()
        flash(f"Club '{club.label}' updated successfully!", "success")
        return redirect(url_for("admin.clubs_list"))
    elif request.method == "GET":
        form.label.data = club.label
        form.href.data = club.href
        form.logo.data = club.logo
    return render_template("admin/parametrization/links/club_form.html", form=form, action="Edit")


@admin_bp.route("/parametrization/clubs/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def club_delete(id):
    """Delete club."""
    club = Club.query.get_or_404(id)
    label = club.label
    db.session.delete(club)
    db.session.commit()
    flash(f"Club '{label}' deleted successfully!", "success")
    return redirect(url_for("admin.clubs_list"))


# ============================================================================
# SETTINGS
# ============================================================================

@admin_bp.route("/parametrization/settings", methods=["GET"])
@login_required
@admin_required
def settings_list():
    """List all settings."""
    settings = Setting.query.order_by(Setting.key).all()
    return render_template("admin/parametrization/settings_list.html", settings=settings)


@admin_bp.route("/parametrization/settings/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def setting_edit(id):
    """Edit setting."""
    setting = Setting.query.get_or_404(id)
    form = SettingForm()
    if form.validate_on_submit():
        setting.value = form.value.data
        db.session.commit()
        flash(f"Setting '{setting.key}' updated successfully!", "success")
        return redirect(url_for("admin.settings_list"))
    elif request.method == "GET":
        form.value.data = setting.value
    return render_template("admin/parametrization/setting_form.html", form=form, setting=setting, action="Edit")


# ============================================================================
# CALENDAR CATEGORIES
# ============================================================================

@admin_bp.route("/parametrization/calendar-categories", methods=["GET"])
@login_required
@admin_required
def calendar_categories_list():
    """List all calendar categories."""
    categories = CalendarCategory.query.order_by(CalendarCategory.key).all()
    return render_template("admin/parametrization/calendar_categories_list.html", categories=categories)


@admin_bp.route("/parametrization/calendar-categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def calendar_category_edit(id):
    """Edit calendar category."""
    category = CalendarCategory.query.get_or_404(id)
    form = CalendarCategoryForm()
    if form.validate_on_submit():
        category.activity_type = form.activity_type.data
        category.label = form.label.data
        category.color = form.color.data
        db.session.commit()
        flash(f"Category '{category.label}' updated successfully!", "success")
        return redirect(url_for("admin.calendar_categories_list"))
    elif request.method == "GET":
        form.activity_type.data = category.activity_type
        form.label.data = category.label
        form.color.data = category.color
    return render_template("admin/parametrization/calendar_category_form.html", form=form, category=category, action="Edit")
