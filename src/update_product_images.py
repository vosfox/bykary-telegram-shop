import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.product import Product
from src.models.product_image import ProductImage
from src.main import app

# Данные изображений товаров
PRODUCT_IMAGES = {
    1: {  # Футболка с монограммой черная
        'images': [
            '/static/images/futbolka_s_monogrammoy_chernaya_1.webp',
            '/static/images/futbolka_s_monogrammoy_chernaya_2.webp',
            '/static/images/futbolka_s_monogrammoy_chernaya_3.webp'
        ]
    },
    2: {  # Футболка с монограммой белая
        'images': [
            '/static/images/futbolka_s_monogrammoy_belaya_1.webp',
            '/static/images/futbolka_s_monogrammoy_belaya_2.webp',
            '/static/images/futbolka_s_monogrammoy_belaya_3.webp'
        ]
    },
    3: {  # Костюм-полоска Аладдин rosy
        'images': [
            '/static/images/kostyum_poloska_aladdin_rosy_1.webp',
            '/static/images/kostyum_poloska_aladdin_rosy_2.webp',
            '/static/images/kostyum_poloska_aladdin_rosy_3.webp'
        ]
    },
    4: {  # Костюм-полоска Аладдин blue
        'images': [
            '/static/images/kostyum_poloska_aladdin_blue_1.webp',
            '/static/images/kostyum_poloska_aladdin_blue_2.webp',
            '/static/images/kostyum_poloska_aladdin_blue_3.webp'
        ]
    },
    5: {  # Футболка-платье Mama needs champagne розовая
        'images': [
            '/static/images/futbolka_plate_mama_needs_champagne_roz_1.webp',
            '/static/images/futbolka_plate_mama_needs_champagne_roz_2.webp'
        ]
    },
    6: {  # Футболка-платье Mama needs champagne бежевая
        'images': [
            '/static/images/futbolka_plate_mama_needs_champagne_bezh_1.webp',
            '/static/images/futbolka_plate_mama_needs_champagne_bezh_2.webp'
        ]
    },
    7: {  # Футболка-поло в полоску
        'images': [
            '/static/images/futbolka_polo_v_polosku_1.webp',
            '/static/images/futbolka_polo_v_polosku_2.webp'
        ]
    },
    8: {  # Джинсовая куртка-косуха молочная
        'images': [
            '/static/images/dzhinsovaya_kurtka_kosuha_molochnaya_1.webp',
            '/static/images/dzhinsovaya_kurtka_kosuha_molochnaya_2.webp'
        ]
    }
}

def update_product_images():
    """Обновить изображения товаров в базе данных"""
    
    with app.app_context():
        print("🔄 Начинаем обновление изображений товаров...")
        
        # Очищаем существующие изображения
        ProductImage.query.delete()
        print("✅ Очищены старые изображения")
        
        # Добавляем новые изображения для каждого товара
        for product_id, data in PRODUCT_IMAGES.items():
            product = Product.query.get(product_id)
            if not product:
                print(f"⚠️  Товар с ID {product_id} не найден")
                continue
                
            images = data['images']
            print(f"📦 Обновляем товар '{product.name}' ({len(images)} изображений)")
            
            # Обновляем основное изображение в старом поле для совместимости
            if images:
                product.image_url = images[0]
            
            # Добавляем изображения в новую структуру
            for index, image_url in enumerate(images):
                product_image = ProductImage(
                    product_id=product_id,
                    image_url=image_url,
                    is_primary=(index == 0),  # Первое изображение - основное
                    alt_text=f"{product.name} - фото {index + 1}",
                    order_index=index
                )
                db.session.add(product_image)
                print(f"   ✅ Добавлено изображение {index + 1}: {image_url}")
        
        # Сохраняем изменения
        db.session.commit()
        print("\n🎉 Обновление изображений завершено успешно!")
        
        # Проверяем результат
        total_images = ProductImage.query.count()
        print(f"📊 Всего изображений в базе: {total_images}")
        
        # Показываем статистику по товарам
        for product_id in PRODUCT_IMAGES.keys():
            product = Product.query.get(product_id)
            if product:
                image_count = len(product.images)
                print(f"   📦 {product.name}: {image_count} изображений")

if __name__ == '__main__':
    update_product_images()