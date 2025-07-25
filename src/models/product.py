from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(50))
    sizes = db.Column(db.String(100))  # JSON string: ["XS", "S", "M", "L"]
    
    def to_dict(self):
        # Пробуем получить связанные изображения, если не получается - используем основное
        product_images = []
        
        try:
            # Импортируем здесь чтобы избежать циклических импортов
            from src.models.product_image import ProductImage
            
            # Получаем все изображения товара из связанной таблицы
            images_query = ProductImage.query.filter_by(product_id=self.id).order_by(ProductImage.order_index).all()
            
            if images_query:
                product_images = [img.image_url for img in images_query]
            elif self.image_url:
                product_images = [self.image_url]
            else:
                product_images = ['/static/images/placeholder.svg']
                
        except Exception:
            # Если что-то пошло не так, используем основное изображение
            product_images = [self.image_url] if self.image_url else ['/static/images/placeholder.svg']
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'images': product_images,  # Массив всех изображений
            'category': self.category,
            'sizes': self.sizes.split(',') if self.sizes else []
        }

