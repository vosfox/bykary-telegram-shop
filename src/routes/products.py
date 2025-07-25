from flask import Blueprint, jsonify, request
from src.models.product import Product, db
from flask_cors import cross_origin

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
@cross_origin()
def get_products():
    """Получить все товары"""
    category = request.args.get('category')
    
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    
    return jsonify([product.to_dict() for product in products])

@products_bp.route('/products/<int:product_id>', methods=['GET'])
@cross_origin()
def get_product(product_id):
    """Получить товар по ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@products_bp.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    """Получить все категории"""
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([cat[0] for cat in categories if cat[0]])

