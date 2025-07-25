from flask import Blueprint, jsonify, request
from src.models.order import Order, db
from src.models.cart import CartItem
from src.models.product import Product
from flask_cors import cross_origin

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['POST'])
@cross_origin()
def create_order():
    """Создать заказ"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    name = data.get('name')
    phone = data.get('phone')
    city = data.get('city')
    comment = data.get('comment', '')
    
    # Получаем товары из корзины
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        return jsonify({'error': 'Корзина пуста'}), 400
    
    # Вычисляем общую сумму
    total_amount = 0
    for item in cart_items:
        total_amount += item.product.price * item.quantity
    
    # Создаем заказ
    order = Order(
        user_id=user_id,
        name=name,
        phone=phone,
        city=city,
        comment=comment,
        total_amount=total_amount
    )
    
    db.session.add(order)
    
    # Очищаем корзину после оформления заказа
    for item in cart_items:
        db.session.delete(item)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'total_amount': total_amount,
        'message': '✅ Спасибо! Это демо-версия. Для покупки — переходите на bykary.ru'
    })

@orders_bp.route('/orders/<user_id>', methods=['GET'])
@cross_origin()
def get_user_orders(user_id):
    """Получить заказы пользователя"""
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

