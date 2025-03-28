# api_arcane
## Description
L'api_arcane est un ensemble de microservices de gestion immobilière utilisant Flask et PostgreSQL. Elle permet de gérer les utilisateurs, les biens immobiliers et les pièces associées à ces biens. Le système d'authentification est basé sur JWT (JSON Web Token).
## Prérequis
Avant de commencer, assurez-vous que vous avez les éléments suivants installés sur votre machine ou sur un environnement :

Python 3.x (recommandé : version 3.8 ou supérieure) j'ai 3.12.3 
PostgreSQL (version 12 ou supérieure) j'ai 16.8
Pip (gestionnaire de paquets Python)
Postman (outil de test d'API)
Flask et autres dépendances Python nécessaires ( flask, flask_sqlalchemy, flask_jwt_extended).

## Installation:
### Etape1: Création de la base de données (Possibilité d'utiliser autre que postgres)
    sudo -u postgres psql
    CREATE DATABASE immobilier;

#### Etape2: Récupération du code
    git clone https://github.com/salimatacissouma/api_arcane.git
    cd api_arcane
### Etape3: Configuration de la base de données
Dans app.py, adapté cette ligne app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/immobilier' à votre utilisateur si c'est pas postgres. Voici la structure app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/immobilier'

### Etape4: Démarrage des services
    python app.py
l'application est lancé sur http://127.0.0.1:5000
 A partir de là, il est possible tester tous les APIs. Par exemple ( POST http://127.0.0.1:5000/register pour le test de l'enregistrement de l'utilisateur
 , POST http://127.0.0.1:5000/login pour la connexion, PUT http://127.0.0.1:5000/properties/{property_id} pour modifier un bien etc).

En dehors de register et login un token de connexion est nécéssaire pour les autres. Ne pas oublier de récupérer le token de connexion pour le mettre au nievau des autorisations. 
