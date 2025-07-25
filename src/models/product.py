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
    
    # Связь с изображениями
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        # Получаем все изображения товара
        product_images = []
        if self.images:
            # Сортируем по order_index
            sorted_images = sorted(self.images, key=lambda x: x.order_index or 0)
            product_images = [img.image_url for img in sorted_images]
        elif self.image_url:
            product_images = [self.image_url]
        
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

