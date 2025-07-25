import os
import requests
import sys
from urllib.parse import urlparse

# Данные товаров с изображениями
PRODUCTS_DATA = {
    1: {
        'name': 'Футболка с монограммой черная',
        'images': [
            'https://optim.tildacdn.com/stor6533-3332-4562-a162-386530363231/-/format/webp/74776859.jpg.webp',
            'https://optim.tildacdn.com/stor3036-3431-4762-b135-323436626561/-/format/webp/74742756.webp'
        ]
    },
    2: {
        'name': 'Футболка с монограммой белая',
        'images': [
            'https://optim.tildacdn.com/stor3430-3131-4565-b461-643636323166/-/format/webp/71901513.jpg.webp',
            'https://optim.tildacdn.com/stor6633-3366-4533-b733-636162366331/-/format/webp/46327471.webp'
        ]
    },
    3: {
        'name': 'Костюм-полоска Аладдин rosy',
        'images': [
            'https://optim.tildacdn.com/stor3034-6130-4865-b135-313231353033/-/format/webp/68548671.webp',
            'https://optim.tildacdn.com/stor6232-6532-4532-b833-633161626432/-/format/webp/15289657.webp'
        ]
    },
    4: {
        'name': 'Костюм-полоска Аладдин blue',
        'images': [
            'https://optim.tildacdn.com/stor6636-6438-4631-b835-353061393036/-/format/webp/51056772.webp',
            'https://optim.tildacdn.com/stor3365-6439-4634-b230-326462393233/-/format/webp/38720767.jpg.webp'
        ]
    },
    5: {
        'name': 'Футболка-платье Mama needs champagne розовая',
        'images': [
            'https://optim.tildacdn.com/stor6431-3961-4132-a339-623337643562/-/format/webp/66726007.jpg.webp',
            'https://optim.tildacdn.com/stor3961-6438-4230-b865-306437626665/-/contain/938x1408/center/center/-/format/webp/78366020.jpg.webp'
        ]
    },
    6: {
        'name': 'Футболка-платье Mama needs champagne бежевая',
        'images': [
            'https://optim.tildacdn.com/stor3932-3939-4663-b530-656536653431/-/format/webp/85464327.jpg.webp',
            'https://optim.tildacdn.com/stor3236-6636-4637-b762-303835363861/-/contain/938x1408/center/center/-/format/webp/48720399.jpg.webp',
            'https://optim.tildacdn.com/stor3839-3635-4036-b737-666534383239/-/contain/938x1408/center/center/-/format/webp/12057208.jpg.webp'
        ]
    },
    7: {
        'name': 'Футболка-поло в полоску',
        'images': [
            'https://optim.tildacdn.com/stor3461-3061-4532-b763-633164633533/-/format/webp/44890026.jpg.webp',
            'https://optim.tildacdn.com/stor3762-3235-4664-a364-363637303834/-/contain/938x1408/center/center/-/format/webp/83127075.jpg.webp'
        ]
    },
    8: {
        'name': 'Джинсовая куртка-косуха молочная',
        'images': [
            'https://optim.tildacdn.com/stor6361-3566-4638-b539-306530356339/-/format/webp/41270703.jpg.webp',
            'https://optim.tildacdn.com/stor6461-3031-4665-a435-323161356538/-/contain/938x1408/center/center/-/format/webp/26503353.jpg.webp',
            'https://optim.tildacdn.com/stor3861-3136-4164-a438-626430353631/-/format/webp/11017470.jpg.webp'
        ]
    }
}

def download_product_images():
    """Скачать все изображения товаров"""
    
    # Создаем папку для изображений
    images_dir = os.path.join("src", "static", "images")
    os.makedirs(images_dir, exist_ok=True)
    
    print("🔄 Начинаем скачивание изображений товаров BY KARY...")
    print(f"📁 Папка назначения: {os.path.abspath(images_dir)}")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for product_id, product_data in PRODUCTS_DATA.items():
        product_name = product_data['name']
        images = product_data['images']
        
        print(f"\n📦 ТОВАР {product_id}: {product_name}")
        print(f"   🖼️  Изображений: {len(images)}")
        
        for index, image_url in enumerate(images, 1):
            try:
                # Генерируем имя файла
                filename = f"product_{product_id}_{index}.webp"
                local_path = os.path.join(images_dir, filename)
                
                print(f"   ⬇️  Скачиваем изображение {index}...")
                
                # Добавляем заголовки для обхода блокировок
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                # Скачиваем файл
                response = requests.get(image_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Сохраняем файл
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"      ✅ Сохранено: {filename} ({file_size:,} байт)")
                success_count += 1
                
            except Exception as e:
                print(f"      ❌ Ошибка: {str(e)}")
                error_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТ:")
    print(f"   ✅ Успешно скачано: {success_count} изображений")
    print(f"   ❌ Ошибок: {error_count}")
    
    if success_count > 0:
        print(f"\n🎉 СЛЕДУЮЩИЙ ШАГ:")
        print(f"   1. Запустите сервер: python src/main.py") 
        print(f"   2. Откройте в браузере: http://localhost:5000/update-images")
        print(f"   3. Или запустите: python src/update_product_images.py")
        print(f"\n💫 После этого в каталоге появятся красивые галереи изображений!")

if __name__ == '__main__':
    download_product_images()