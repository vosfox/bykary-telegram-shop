from src.models.user import db

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)  # Основное изображение
    alt_text = db.Column(db.String(200))  # Альтернативный текст для SEO
    order_index = db.Column(db.Integer, default=0)  # Порядок отображения
    
    # Отношение к продукту
    product = db.relationship('Product', backref=db.backref('images', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'image_url': self.image_url,
            'is_primary': self.is_primary,
            'alt_text': self.alt_text,
            'order_index': self.order_index
        }
    
    def __repr__(self):
        return f'<ProductImage {self.id}: {self.image_url}>'