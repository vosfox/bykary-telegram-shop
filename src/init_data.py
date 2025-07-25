import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.product import Product, db

def init_products():
    """Инициализация товаров для демо-магазина"""
    
    products_data = [
        {
            'name': 'Футболка с монограммой черная',
            'description': 'Стильная футболка с монограммой ByKary',
            'price': 5900.0,
            'image_url': '/static/images/product_1_1.webp',
            'category': 'Топы/Футболки',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Футболка с монограммой белая',
            'description': 'Элегантная белая футболка с монограммой',
            'price': 5900.0,
            'image_url': '/static/images/product_2_1.webp',
            'category': 'Топы/Футболки',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Костюм-полоска Аладдин rosy',
            'description': 'Нежный костюм в полоску розового цвета',
            'price': 15900.0,
            'image_url': '/static/images/product_3_1.webp',
            'category': 'Костюмы',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Костюм-полоска Аладдин blue',
            'description': 'Стильный костюм в полоску голубого цвета',
            'price': 15900.0,
            'image_url': '/static/images/product_4_1.webp',
            'category': 'Костюмы',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Футболка-платье Mama needs champagne розовая',
            'description': 'Удобное платье-футболка с принтом',
            'price': 6900.0,
            'image_url': '/static/images/product_5_1.webp',
            'category': 'Платья',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Футболка-платье Mama needs champagne бежевая',
            'description': 'Стильное платье-футболка бежевого цвета',
            'price': 6900.0,
            'image_url': '/static/images/product_6_1.webp',
            'category': 'Платья',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Футболка-поло в полоску',
            'description': 'Классическая поло в полоску',
            'price': 6900.0,
            'image_url': '/static/images/product_7_1.webp',
            'category': 'Топы/Футболки',
            'sizes': 'XS,S,M,L'
        },
        {
            'name': 'Джинсовая куртка-косуха молочная',
            'description': 'Стильная джинсовая куртка молочного цвета',
            'price': 12900.0,
            'image_url': '/static/images/product_8_1.webp',
            'category': 'Верхняя одежда',
            'sizes': 'XS,S,M,L'
        }
    ]
    
    with app.app_context():
        # Очищаем существующие товары
        Product.query.delete()
        
        # Добавляем новые товары
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Добавлено {len(products_data)} товаров в базу данных")

if __name__ == '__main__':
    init_products()

