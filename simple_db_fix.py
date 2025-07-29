# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app, db
from src.models.product import Product

def fix_database():
    with app.app_context():
        # Пересоздаем все таблицы
        db.drop_all()
        db.create_all()
        
        # Добавляем товары
        products = [
            Product(name='Футболка с монограммой черная', description='Стильная футболка', price=5900.0, image_url='/static/images/product_1_1.webp', category='Топы', sizes='XS,S,M,L'),
            Product(name='Футболка с монограммой белая', description='Белая футболка', price=5900.0, image_url='/static/images/product_2_1.webp', category='Топы', sizes='XS,S,M,L'),
            Product(name='Костюм Аладдин rosy', description='Розовый костюм', price=15900.0, image_url='/static/images/product_3_1.webp', category='Костюмы', sizes='XS,S,M,L'),
            Product(name='Костюм Аладдин blue', description='Голубой костюм', price=15900.0, image_url='/static/images/product_4_1.webp', category='Костюмы', sizes='XS,S,M,L'),
            Product(name='Платье Mama needs champagne розовое', description='Розовое платье', price=6900.0, image_url='/static/images/product_5_1.webp', category='Платья', sizes='XS,S,M,L'),
            Product(name='Платье Mama needs champagne бежевое', description='Бежевое платье', price=6900.0, image_url='/static/images/product_6_1.webp', category='Платья', sizes='XS,S,M,L'),
            Product(name='Футболка-поло в полоску', description='Полосатая поло', price=6900.0, image_url='/static/images/product_7_1.webp', category='Топы', sizes='XS,S,M,L'),
            Product(name='Джинсовая куртка молочная', description='Молочная куртка', price=12900.0, image_url='/static/images/product_8_1.webp', category='Куртки', sizes='XS,S,M,L')
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        print("Database fixed! Added", len(products), "products")

if __name__ == '__main__':
    fix_database()