from flask import Flask, jsonify, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, set_access_cookies, JWTManager, jwt_required, get_jwt_identity, get_jwt
import time
import traceback
import os
from functools import wraps
from datetime import datetime
from datetime import timedelta
from datetime import timezone

app = Flask(__name__)


healthy=True

ACCESS_EXPIRES = timedelta(hours=1)

db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'cockroachdb://{db_username}:{db_password}@cockroachdb-public:26257/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_COOKIE_NAME"] = "jwt"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Strict" 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config['JWT_VERIFY_SUB'] = False        #IMP

jwt = JWTManager(app)

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

# Callback function to check if a JWT exists in the db blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


def content_type_json_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400
        return f(*args, **kwargs)
    return decorated_function

@app.route('/validate', methods=['GET'])
@jwt_required()
def validate():
    try:
        current_user_id = get_jwt_identity()
        response = jsonify({"message": "Valid token"})
        response.headers['X-User-ID'] = current_user_id
        return response, 200
    
    except ExpiredSignatureError:
        return jsonify({"message": "Expired token"}), 401
    except InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
    except Exception:
        traceback.print_exc()

@app.route('/authentication/registration', methods=["POST"])
@content_type_json_required
def registration():
    try:
        data=request.get_json()
        username=data.get("username")
        password=data.get("password")
        newUser = Users(username=username, password=password)
        db.session.add(newUser)
        db.session.commit()
        return jsonify({"message": "Registered!"}) 
    except Exception as e:
        traceback.print_exc()
        return "Bad request", 400

@app.route('/authentication/logout', methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    response = redirect('/authentication/login')
    #response.set_cookie('jwt', ' ', expires=0, path="/")
    return response

@app.route('/authentication/login', methods=["GET"])
def loginPage():
    return "You should login first"

@app.route('/authentication/login', methods=["POST"])
@content_type_json_required
def login():
    time.sleep(3)
    try:
        data=request.get_json()
        username=data.get("username")
        password=data.get("password")
        user=Users.query.filter(Users.username==username, Users.password==password).first()
        if user is None:
            return jsonify({"message": "Login error"})
        else:
            access_token = create_access_token(identity=user.id)
            response = make_response(jsonify({"msg": "Login successful"}))
            set_access_cookies(response, access_token)
            return response
    except:
        traceback.print_exc()
        return "Bad request", 400

@app.route('/authentication/whoami', methods=["GET"])
@jwt_required()
def whoami():
    current_user_id = request.headers.get('X-User-ID')
    current_user=Users.query.filter(Users.id==current_user_id).first()
    return jsonify({"Logged_in_as": current_user.username})

@app.route('/health', methods=["GET"])
def isHealthy():
    global healthy
    if healthy:
        return "Healthy", 200
    else:
        return "Unhealthy", 500

@app.route('/authentication/fail', methods=["GET"])
def fail():
    global healthy
    healthy=False
    return "Ok", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, ssl_context=("/certs/server.crt", "/certs/server.key"))