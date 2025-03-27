from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime



app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/immobilier'

# Configuration du secret pour JWT
app.config['JWT_SECRET_KEY'] = 'mysecretkey'

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)
jwt = JWTManager(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_owner = db.Column(db.Boolean, default=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    properties = db.relationship('Property', backref='owner', lazy=True)


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pieces = db.relationship('Piece', backref='property', lazy=True)


class Piece(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
# Route pour la page d'accueil
@app.route('/')
def home():
    return 'Welcome to the Immobilier API!'

# Réinitialisé la base de données
def reset_database():
    with app.app_context():
        db.drop_all()
        db.session.commit()  # S'assurer que la suppression est bien prise en compte
        db.create_all()
        print("Base de données réinitialisée avec succès !")


# Routes pour l'enregistrement & la connexion
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        lastname=data['lastname'], 
        firstname=data['firstname'], 
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d'),
        email=data['email'],
        password=data['password'],
        is_owner=data.get('is_owner', False)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur ajouté !'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.password == data['password']:  # Ne pas oublier de vérifier le hash en production
        access_token = create_access_token(identity={'id': user.id, 'is_owner': user.is_owner})
        return jsonify({'message': 'Vous êtes connecté !', 'access_token': access_token})
    return jsonify({'message': 'Identifiants invalides'}), 401

# Exécution principale
if __name__ == '__main__':
    reset_database()
    app.run(debug=True)