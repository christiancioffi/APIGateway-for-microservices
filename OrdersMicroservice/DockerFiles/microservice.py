from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import time
import traceback
import os
from datetime import datetime
from functools import wraps


app = Flask(__name__)

db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'cockroachdb://{db_username}:{db_password}@cockroachdb-public:26257/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

healthy=True

class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    productid = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    date = db.Column(db.TIMESTAMP)
    userid = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'productid': self.productid,
            'quantity': self.quantity,
            'date': self.date.isoformat(),
            'userid': self.userid
        }

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

def content_type_json_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400
        return f(*args, **kwargs)
    return decorated_function

@app.route('/orders', methods=["GET"])
def orders():
    time.sleep(3)
    userID=request.headers.get('X-User-ID')
    orders=Orders.query.filter(Orders.userid==userID).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/microservice/orders/add', methods=["POST"])
@content_type_json_required
def addOrder():
    time.sleep(3)
    data = request.get_json()
    productID=data.get("productID")
    quantity=data.get("quantity")
    userID=data.get("userID")
    date=datetime.utcnow()
    newOrder=Orders(productid=productID, quantity=quantity, userid=userID, date=date)
    try:
        db.session.add(newOrder)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Order added successfully!"})


@app.route('/health', methods=["GET"])
def isHealthy():
    global healthy
    if healthy:
        return "Healthy", 200
    else:
        return "Unhealthy", 500

@app.route('/orders/fail', methods=["GET"])
def fail():
    global healthy
    healthy=False
    return "Ok", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, ssl_context=("/certs/server.crt", "/certs/server.key"))