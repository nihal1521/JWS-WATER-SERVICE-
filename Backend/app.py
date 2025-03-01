from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jws_water_service.db'
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'driver', 'dealer', 'admin'

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='incomplete')  # 'complete', 'incomplete'
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(200), nullable=False)
    dealer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Create database tables
with app.app_context():
    db.create_all()

# Helper Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"message": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity={"username": user.username, "role": user.role})
    return jsonify({"access_token": access_token, "role": user.role}), 200

@app.route('/locations', methods=['GET', 'POST'])
@jwt_required()
def handle_locations():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        if current_user['role'] != 'admin':
            return jsonify({"message": "Unauthorized"}), 403

        data = request.json
        new_location = Location(name=data['name'], address=data['address'], driver_id=data.get('driver_id'))
        db.session.add(new_location)
        db.session.commit()
        return jsonify({"message": "Location added"}), 201

    locations = Location.query.all()
    return jsonify([{"id": loc.id, "name": loc.name, "address": loc.address, "status": loc.status} for loc in locations]), 200

@app.route('/locations/<int:location_id>/complete', methods=['PUT'])
@jwt_required()
def mark_location_complete(location_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'driver':
        return jsonify({"message": "Unauthorized"}), 403

    location = Location.query.get(location_id)
    if not location:
        return jsonify({"message": "Location not found"}), 404

    location.status = 'complete'
    db.session.commit()
    return jsonify({"message": "Location marked as complete"}), 200

@app.route('/deals', methods=['GET', 'POST'])
@jwt_required()
def handle_deals():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        if current_user['role'] != 'dealer':
            return jsonify({"message": "Unauthorized"}), 403

        data = request.json
        new_deal = Deal(details=data['details'], dealer_id=User.query.filter_by(username=current_user['username']).first().id)
        db.session.add(new_deal)
        db.session.commit()
        return jsonify({"message": "Deal added"}), 201

    deals = Deal.query.all()
    return jsonify([{"id": deal.id, "details": deal.details} for deal in deals]), 200

if __name__ == '__main__':
    app.run(debug=True)