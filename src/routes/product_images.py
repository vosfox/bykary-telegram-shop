from flask import Blueprint, jsonify, request
from src.models.product_image import ProductImage, db
from src.models.product import Product
from flask_cors import cross_origin

product_images_bp = Blueprint('product_images', __name__)

@product_images_bp.route('/products/<int:product_id>/images', methods=['GET'])
@cross_origin()
def get_product_images(product_id):
    """Получить все изображения товара"""
    images = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.order_index).all()
    return jsonify([img.to_dict() for img in images])

@product_images_bp.route('/products/<int:product_id>/images', methods=['POST'])
@cross_origin()
def add_product_image(product_id):
    """Добавить изображение к товару"""
    data = request.get_json()
    
    # Проверяем, существует ли товар
    product = Product.query.get_or_404(product_id)
    
    image_url = data.get('image_url', '')
    is_primary = data.get('is_primary', False)
    alt_text = data.get('alt_text', '')
    order_index = data.get('order_index', 0)
    
    # Если это основное изображение, убираем флаг у других
    if is_primary:
        ProductImage.query.filter_by(product_id=product_id, is_primary=True).update({'is_primary': False})
    
    # Создаем новое изображение
    new_image = ProductImage(
        product_id=product_id,
        image_url=image_url,
        is_primary=is_primary,
        alt_text=alt_text,
        order_index=order_index
    )
    
    db.session.add(new_image)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'image': new_image.to_dict()
    })

@product_images_bp.route('/products/<int:product_id>/images/<int:image_id>', methods=['PUT'])
@cross_origin()
def update_product_image(product_id, image_id):
    """Обновить изображение товара"""
    image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    data = request.get_json()
    
    # Если устанавливаем как основное, убираем флаг у других
    if data.get('is_primary', False):
        ProductImage.query.filter_by(product_id=product_id, is_primary=True).update({'is_primary': False})
    
    # Обновляем поля
    if 'image_url' in data:
        image.image_url = data['image_url']
    if 'is_primary' in data:
        image.is_primary = data['is_primary']
    if 'alt_text' in data:
        image.alt_text = data['alt_text']
    if 'order_index' in data:
        image.order_index = data['order_index']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'image': image.to_dict()
    })

@product_images_bp.route('/products/<int:product_id>/images/<int:image_id>', methods=['DELETE'])
@cross_origin()
def delete_product_image(product_id, image_id):
    """Удалить изображение товара"""
    image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({'success': True})

@product_images_bp.route('/products/<int:product_id>/images/reorder', methods=['POST'])
@cross_origin()
def reorder_product_images(product_id):
    """Изменить порядок изображений товара"""
    data = request.get_json()
    image_orders = data.get('orders', [])  # [{'id': 1, 'order_index': 0}, ...]
    
    for item in image_orders:
        image_id = item.get('id')
        order_index = item.get('order_index', 0)
        
        image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
        if image:
            image.order_index = order_index
    
    db.session.commit()
    
    return jsonify({'success': True})