from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpeg')
    password = db.Column(db.String(60), nullable=False)
    albums = db.relationship('Album', backref='author', lazy=True)
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.String(10), unique=False, nullable=False)
    cover_pic = db.Column(db.String(20), nullable=False, default='default.jpeg')
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    likes = db.Column(db.Integer, nullable= False)
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpeg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    likes = db.Column(db.Integer, nullable= False)


class LikePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_liked = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)


class LikeAlbum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_liked = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    album_id = db.Column(db.Integer, nullable=False)


