#!/usr/bin/env python3
"""
Скрипт для исправления базы данных
Создает все необходимые таблицы и заполняет данными
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app, db
from src.models.product import Product
from src.models.user import User
from src.models.cart import CartItem
from src.models.order import Order

# Проверяем есть ли product_images модель
try:
    from src.models.product_image import ProductImage
    HAS_PRODUCT_IMAGES = True
    print("OK ProductImage модель найдена")
except ImportError:
    HAS_PRODUCT_IMAGES = False
    print("⚠️ ProductImage модель не найдена, пропускаем")

def recreate_database():
    """Пересоздание базы данных с нуля"""
    print("🔄 Пересоздание базы данных...")
    
    with app.app_context():
        # Удаляем все таблицы
        db.drop_all()
        print("❌ Старые таблицы удалены")
        
        # Создаем все таблицы заново
        db.create_all()
        print("✅ Новые таблицы созданы")
        
        # Добавляем товары
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
                'description': 'Стильное бежевое платье-футболка',
                'price': 6900.0,
                'image_url': '/static/images/product_6_1.webp',
                'category': 'Платья',
                'sizes': 'XS,S,M,L'
            },
            {
                'name': 'Футболка-поло в полоску',
                'description': 'Классическая полосатая футболка-поло',
                'price': 6900.0,
                'image_url': '/static/images/product_7_1.webp',
                'category': 'Топы/Футболки',
                'sizes': 'XS,S,M,L'
            },
            {
                'name': 'Джинсовая куртка-косуха молочная',
                'description': 'Стильная молочная джинсовая куртка',
                'price': 12900.0,
                'image_url': '/static/images/product_8_1.webp',
                'category': 'Куртки',
                'sizes': 'XS,S,M,L'
            }
        ]
        
        # Добавляем товары в базу
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
        
        # Если есть модель ProductImage, добавляем доп. изображения
        if HAS_PRODUCT_IMAGES:
            print("📸 Добавляем дополнительные изображения...")
            
            # Получаем товары для добавления доп. изображений
            db.session.commit()  # Сначала сохраняем товары
            
            # Добавляем доп. изображения для некоторых товаров
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
        
        # Сохраняем все изменения
        db.session.commit()
        print(f"✅ Добавлено {len(products_data)} товаров")
        
        if HAS_PRODUCT_IMAGES:
            print(f"✅ Добавлено {len(additional_images)} дополнительных изображений")
        
        print("🎉 База данных успешно восстановлена!")

if __name__ == '__main__':
    recreate_database()