from functools import wraps

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Product, ProductImage
from app.shop import shop
from app.shop.forms import MAX_PHOTOS, ProductForm
from app.storage import InvalidImage, get_storage, prepare_image, save_image


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def can_manage(product):
    return current_user.is_authenticated and (
        current_user.is_admin or current_user.id == product.seller_id
    )


def newest_first():
    return (Product.created_at.desc(), Product.id.desc())


@shop.route("/shop")
def index():
    products = db.session.execute(
        db.select(Product)
        .where(Product.is_verified.is_(True), Product.is_available.is_(True))
        .order_by(*newest_first())
    ).scalars().all()
    return render_template(
        "shop/shop.html",
        team_products=[p for p in products if p.is_official_clothing],
        used_products=[p for p in products if not p.is_official_clothing],
    )


@shop.route("/shop/mine")
@login_required
def mine():
    products = db.session.execute(
        db.select(Product).where(Product.seller_id == current_user.id).order_by(*newest_first())
    ).scalars().all()
    return render_template("shop/list.html", title="I miei annunci", products=products, show_status=True)


@shop.route("/shop/pending")
@admin_required
def pending():
    products = db.session.execute(
        db.select(Product).where(Product.is_verified.is_(False)).order_by(*newest_first())
    ).scalars().all()
    return render_template(
        "shop/list.html",
        title="Annunci da verificare",
        products=products,
        show_status=True,
        empty_message="Nessun annuncio in attesa di verifica.",
    )


@shop.route("/shop/create", methods=["GET", "POST"])
@login_required
def create():
    form = ProductForm()
    if form.validate_on_submit():
        files = [f for f in form.photos.data or [] if f and f.filename]
        if len(files) > MAX_PHOTOS:
            flash(f"Puoi caricare al massimo {MAX_PHOTOS} foto.", "error")
            return render_template("shop/create.html", form=form)
        try:
            prepared = [prepare_image(f) for f in files]
        except InvalidImage as exc:
            flash(str(exc), "error")
            return render_template("shop/create.html", form=form)

        # Only admins can list official clothing; their own listings need no review.
        is_admin = current_user.is_admin
        product = Product(
            seller_id=current_user.id,
            name=form.name.data,
            category=form.category.data,
            size=form.size.data or None,
            price=form.price.data,
            description=form.description.data,
            contact_phone=form.contact_phone.data or None,
            is_official_clothing=bool(is_admin and form.is_official_clothing.data),
            is_verified=is_admin,
        )
        db.session.add(product)
        db.session.flush()  # the id names the product's photo folder
        prefix = product.storage_prefix
        try:
            for item in prepared:
                product.images.append(ProductImage(filename=save_image(prefix, item)))
            db.session.commit()
        except Exception:
            db.session.rollback()
            get_storage().delete_prefix(prefix)
            current_app.logger.exception("Product creation failed")
            flash("Non è stato possibile salvare l'annuncio.", "error")
        else:
            if product.is_verified:
                flash("Articolo pubblicato.", "success")
            else:
                flash("Annuncio salvato: sarà pubblicato dopo la verifica di un amministratore.", "success")
            return redirect(url_for("shop.detail", product_id=product.id))
    return render_template("shop/create.html", form=form)


@shop.route("/shop/<int:product_id>")
def detail(product_id):
    product = db.get_or_404(Product, product_id)
    if not product.is_verified and not can_manage(product):
        abort(404)
    return render_template("shop/detail.html", product=product, can_manage=can_manage(product))


@shop.route("/shop/<int:product_id>/verify", methods=["POST"])
@admin_required
def verify(product_id):
    product = db.get_or_404(Product, product_id)
    product.is_verified = True
    db.session.commit()
    flash("Annuncio verificato e pubblicato.", "success")
    return redirect(url_for("shop.detail", product_id=product.id))


@shop.route("/shop/<int:product_id>/sold", methods=["POST"])
@login_required
def toggle_sold(product_id):
    product = db.get_or_404(Product, product_id)
    if not can_manage(product):
        abort(403)
    product.is_available = not product.is_available
    db.session.commit()
    flash("Articolo di nuovo disponibile." if product.is_available else "Articolo segnato come venduto.", "success")
    return redirect(url_for("shop.detail", product_id=product.id))


@shop.route("/shop/<int:product_id>/delete", methods=["POST"])
@login_required
def delete(product_id):
    product = db.get_or_404(Product, product_id)
    if not can_manage(product):
        abort(403)
    prefix = product.storage_prefix
    db.session.delete(product)
    db.session.commit()
    get_storage().delete_prefix(prefix)
    flash("Annuncio eliminato.", "success")
    return redirect(url_for("shop.mine"))
