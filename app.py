from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db' 
app.app_context().push()


db = SQLAlchemy(app)

class Product(db.Model):
    # database schema
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # serializer 
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price
        }
    
# db.create_all()  # to create schema

@app.route('/products', methods=['GET'])
def get_products():
    limit = request.args.get('limit', 10)
    offset = request.args.get('offset', 0)
    products = Product.query.limit(limit).offset(offset).all()  # limit and offset added for pagination
    return jsonify({'data': [product.serialize() for product in products], 'message': 'Product Fetched Successfully'}), 200

@app.route('/add-products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data:  # validation if data is empty dict
        return jsonify({"error": "Request data is missing"}), 400
    # data type validation
    if not isinstance(data['title'], str):
        return jsonify({'error': 'Invalid title, it must be a non-empty string'}), 400
    
    if not isinstance(data['description'], str):
        return jsonify({'error': 'Invalid description, it must be a non-empty string'}), 400

    if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
        return jsonify({'error': 'Invalid price, it must be a positive number'}), 400
    
    new_product = Product(
        title=data['title'],
        description=data['description'],
        price=data['price']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'data': new_product.serialize(), 'message': 'New Product Entry'}), 200

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({'data': product.serialize(), 'message': f'product id {id} details fetched successfully'}), 200

@app.route('/product/<int:id>', methods = ['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    product.title = data['title']
    product.description = data['description']
    product.price = data['price']
    db.session.commit()
    return jsonify({'data': product.serialize(), 'message': f'product id {id} updated successfully'}), 200

@app.route('/delete-product/<int:id>', methods = ['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product is deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
