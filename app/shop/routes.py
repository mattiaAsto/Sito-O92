from flask import render_template

from app.extensions import db
from app.models import Product
from app.shop import shop


@shop.route("/shop")
def index():
    products = db.session.execute(
        db.select(Product)
        .where(Product.is_available.is_(True))
        .order_by(Product.category, Product.name)
    ).scalars().all()
    team_products = [product for product in products if product.listing_type == "team"]
    used_products = [product for product in products if product.listing_type == "used"]
    return render_template(
        "shop/shop.html",
        team_products=team_products,
        used_products=used_products,
    )
