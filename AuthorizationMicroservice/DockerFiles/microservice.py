from flask import Flask, jsonify, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
import time
import traceback
import os
from functools import wraps

app = Flask(__name__)


healthy=True

db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'cockroachdb://{db_username}:{db_password}@cockroachdb-public:26257/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


@app.route('/validate', methods=['GET'])
def validate():
    try:
        time.sleep(3)
        print(dict(request.headers))
        current_user_id = request.headers.get('X-User-ID')
        current_user=Users.query.filter(Users.id==current_user_id).first()
        if current_user.username=="admin":
            response = jsonify({"message": "User authorized"})
            response.headers['X-User-Role'] = "admin"
            return response, 200
        else:
            return jsonify({"message": "User unauthorized"}), 401
    except Exception:
        traceback.print_exc()

@app.route('/health', methods=["GET"])
def isHealthy():
    global healthy
    if healthy:
        return "Healthy", 200
    else:
        return "Unhealthy", 500

@app.route('/authorization/fail', methods=["GET"])
def fail():
    global healthy
    healthy=False
    return "Ok", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, ssl_context=("/certs/server.crt", "/certs/server.key"))