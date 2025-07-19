from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import time
import traceback
import os
from functools import wraps
from sqlalchemy import DECIMAL
import datetime
import requests

app = Flask(__name__)


db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'cockroachdb://{db_username}:{db_password}@cockroachdb-public:26257/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

healthy=True

class Products(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(50))
    price=db.Column(DECIMAL(10, 2))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description
        }

def content_type_json_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400
        return f(*args, **kwargs)
    return decorated_function

@app.route('/products', methods=["GET"])
def products():
    time.sleep(3)
    products=Products.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/products/admin', methods=["GET"])
def admin_product():
    #print(dict(request.headers))
    special_product = {
        "id": 99999,
        "name": "Admin Special Product",
        "description": "A special product exclusive for admin.",
        "price": 999.99,
        "user_id": request.headers.get('X-User-ID'),
        "user_role": request.headers.get('X-User-Role')
    }
    return jsonify(special_product),200

@app.route('/products/<int:productID>/buy', methods=["POST"])
@content_type_json_required
def buy(productID):

    data=request.get_json()
    user_id=request.headers.get('X-User-ID')
    url="https://orders-microservice/microservice/orders/add"
    body = {
        "productID": productID,
        "quantity": data.get("quantity"),
        "userID": user_id
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=body, headers=headers, verify=False)
        
        if response.status_code == 200:
            return jsonify({"message": response.json()})
        else:
            return jsonify({"error": "Failed to register order", "status": response.status_code}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {e}"}), response.status_code
    except Exception as e:
        traceback.print_exc()
        return "Bad request", 400


@app.route('/health', methods=["GET"])
def isHealthy():
    global healthy
    if healthy:
        return "Healthy", 200
    else:
        return "Unhealthy", 500

@app.route('/products/fail', methods=["GET"])
def fail():
    global healthy
    healthy=False
    return "Ok", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, ssl_context=("/certs/server.crt", "/certs/server.key"))
