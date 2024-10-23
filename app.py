from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db' 
app.config['JWT_SECRET_KEY'] = "6941f7b18bd546108d25e6c724ff8e1f"
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.app_context().push()

db = SQLAlchemy(app)
jwt = JWTManager(app)

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

# to create secrete key I followed following steps:

# import uuid
# uuid.uuid4().hex

users = {
    "username": "admin",
    "password": "admin123"
}

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    print(password)
    if username != users['username'] or password != users['password']:
        return jsonify({"msg": "Bad username or password"}), 401
    
    # Create and return JWT token (login successful)
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# public request
@app.route('/products', methods=['GET'])
def get_products():
    limit = request.args.get('limit', 10)
    offset = request.args.get('offset', 0)
    products = Product.query.limit(limit).offset(offset).all()  # limit and offset added for pagination
    return jsonify({'data': [product.serialize() for product in products], 'message': 'Product Fetched Successfully'}), 200

# jwt auth request
@app.route('/add-products', methods=['POST'])
@jwt_required()
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
