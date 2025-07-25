import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.products import products_bp
from src.routes.cart import cart_bp
from src.routes.orders import orders_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Включаем CORS для всех маршрутов
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(cart_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Импортируем все модели для создания таблиц
from src.models.product import Product
from src.models.cart import CartItem
from src.models.order import Order

with app.app_context():
    db.create_all()

@app.route('/init')
def init_db():
    """Инициализация базы данных"""
    try:
        from src.init_data import init_products
        init_products()
        return "База данных обновлена! Товары добавлены с изображениями."
    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/download-images')
def download_images():
    """Скачать изображения товаров с интернета"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from download_product_images import download_product_images
        download_product_images()
        return "✅ Изображения товаров скачаны успешно!"
    except Exception as e:
        return f"❌ Ошибка скачивания изображений: {str(e)}"

@app.route('/setup-images')
def setup_images():
    """Полная настройка изображений: скачать + обновить базу"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from download_product_images import download_product_images
        
        # Сначала скачиваем изображения
        download_product_images()
        
        # Потом инициализируем базу с товарами
        from src.init_data import init_products
        init_products()
        
        return "🎉 Изображения товаров скачаны и база обновлена! Галереи готовы!"
    except Exception as e:
        return f"❌ Ошибка настройки изображений: {str(e)}"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
