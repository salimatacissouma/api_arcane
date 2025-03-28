from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime



app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/immobilier'

# Configuration du secret pour JWT
app.config['JWT_SECRET_KEY'] = 'mysecretkey'

# Initialisation de SQLAlchemy & JWTManager
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


@app.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    user_identity = get_jwt_identity()
    user = User.query.get_or_404(user_identity['id'])
    data = request.get_json()

    # Mise à jour des champs modifiables
    if 'lastname' in data:
        user.lastname = data['lastname']

    if 'firstname' in data:
        user.firstname = data['firstname']

    if 'date_of_birth' in data:
        try:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Format de date invalide, utilisez YYYY-MM-DD'}), 400

    db.session.commit()

    return jsonify({'message': 'Informations mises à jour avec succès !'})


@app.route('/properties', methods=['POST'])
@jwt_required()
def add_property():
    user = get_jwt_identity()
    data = request.get_json()

    property = Property(
        name=data['name'],
        description=data['description'],
        type=data['type'],
        city=data['city'],
        owner_id=user['id']
    )

    db.session.add(property)
    db.session.commit()
    
    return jsonify({'message': 'Propriété ajouté !'}), 201


@app.route('/properties/<int:property_id>', methods=['PUT'])
@jwt_required()
def update_property(property_id):    
    user = get_jwt_identity()
    property = Property.query.get_or_404(property_id)

    if property.owner_id != user['id']:
        return jsonify({'message': 'Vous ne pouvez modifier que vos propres biens'}), 403
    
    data = request.get_json()
    for key, value in data.items():
        setattr(property, key, value)
    
    db.session.commit()
    
    return jsonify({'message': 'Propriété mis à jour !'})


@app.route('/properties', methods=['GET'])
def get_properties():
    properties = Property.query.all()
    
    return jsonify([{
        'id': p.id,
        'nom': p.name,
        'ville': p.city,
        'propriétaire': p.owner_id
    } for p in properties])


@app.route('/properties/<string:ville>', methods=['GET'])
def get_properties_by_city(ville):
    properties = Property.query.filter_by(city=ville).all()  # Filtrer par ville
    
    if not properties:
        return jsonify({'message': f'Aucun bien trouvé dans la ville de {ville}'}), 404
    
    return jsonify([
        {
            'id': p.id,
            'nom': p.name,
            'ville': p.city,
            'propriétaire': p.owner_id
        } for p in properties
    ])


@app.route('/properties/<int:property_id>/pieces', methods=['POST'])
@jwt_required()
def add_piece(property_id):    
    data = request.get_json()

    piece = Piece(
        name=data['name'],
        description=data['description'],
        property_id=property_id
    )

    db.session.add(piece)
    db.session.commit()
    return jsonify({'message': 'Pièce ajoutée à la propriété !'}), 201

@app.route('/properties/<int:property_id>/pieces', methods=['GET'])
def get_pieces(property_id):
    property = Property.query.get_or_404(property_id)
    
    pieces = property.pieces
    
    return jsonify([{
        'id': piece.id,
        'nom': piece.name,
        'description': piece.description
    } for piece in pieces])



# Exécution principale
if __name__ == '__main__':
    #reset_database() #Décommenter cette ligne lors de la prémière exécution
    app.run(debug=True)