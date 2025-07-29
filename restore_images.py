import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app, db
from src.models.product import Product
from src.models.product_image import ProductImage

with app.app_context():
    # Очищаем product_images
    ProductImage.query.delete()
    
    # Добавляем дополнительные изображения как в оригинале
    additional_images = [
        (1, '/static/images/product_1_2.webp'),
        (2, '/static/images/product_2_2.webp'),
        (3, '/static/images/product_3_2.webp'),
        (4, '/static/images/product_4_2.webp'),
        (5, '/static/images/product_5_2.webp'),
        (6, '/static/images/product_6_2.webp'),
        (6, '/static/images/product_6_3.webp'),
        (7, '/static/images/product_7_2.webp'),
        (8, '/static/images/product_8_2.webp'),
        (8, '/static/images/product_8_3.webp'),
    ]
    
    for product_id, image_url in additional_images:
        image = ProductImage(product_id=product_id, image_url=image_url)
        db.session.add(image)
    
    db.session.commit()
    print('Restored', len(additional_images), 'additional images')