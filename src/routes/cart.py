from flask import Blueprint, jsonify, request
from src.models.cart import CartItem, db
from src.models.product import Product
from flask_cors import cross_origin

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart/<user_id>', methods=['GET'])
@cross_origin()
def get_cart(user_id):
    """Получить корзину пользователя"""
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([item.to_dict() for item in cart_items])

@cart_bp.route('/cart', methods=['POST'])
@cross_origin()
def add_to_cart():
    """Добавить товар в корзину"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    size = data.get('size')
    quantity = data.get('quantity', 1)
    
    # Проверяем, есть ли уже такой товар в корзине
    existing_item = CartItem.query.filter_by(
        user_id=user_id, 
        product_id=product_id, 
        size=size
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            size=size,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'success': True})

@cart_bp.route('/cart/<int:item_id>', methods=['DELETE'])
@cross_origin()
def remove_from_cart(item_id):
    """Удалить товар из корзины"""
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'success': True})

@cart_bp.route('/cart/<int:item_id>', methods=['PUT'])
@cross_origin()
def update_cart_item(item_id):
    """Обновить товар в корзине"""
    data = request.get_json()
    cart_item = CartItem.query.get_or_404(item_id)
    
    if 'quantity' in data:
        cart_item.quantity = data['quantity']
    if 'size' in data:
        cart_item.size = data['size']
    
    db.session.commit()
    return jsonify({'success': True})

