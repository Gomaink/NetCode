from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  
from sqlalchemy import func 

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class PostStars(db.Model):
    __tablename__ = 'post_stars'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    stared_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('post_stars', lazy=True))
    post = db.relationship('Post', backref=db.backref('post_stars', lazy=True))

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/netcode'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    try:
        with app.app_context():
            db.create_all()
        return print(" * Conexão com o banco de dados estabelecida com sucesso!")
    except Exception as e:
        return print(f" * Falha ao conectar ao banco de dados: {e}")
