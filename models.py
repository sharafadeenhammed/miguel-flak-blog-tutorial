from app import db, login
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
import sqlalchemy as sa

# user follower auxilliary table
followers = db.Table(
  'followers',
  db.Column('follower_id', db.Integer,  db.ForeignKey('users.id')),
  db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

# user model class
class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(100), unique = True, index = True)
  email = db.Column(db.String(100), index = True, unique = True)
  password = db.Column(db.String(200))
  last_seen = db.Column(db.DateTime, default=datetime.utcnow, index = True)
  about_me = db.Column(db.String, nullable=True)
  posts = db.relationship(
    'Post',
    backref = 'author',
    lazy = 'dynamic'
  )
  followed = db.relationship(
    'User',
    secondary = followers,
    primaryjoin = (followers.c.follower_id == id),
    secondaryjoin = (followers.c.followed_id == id),
    backref = db.backref('followers', lazy='dynamic'),
    lazy = 'dynamic'
  )
  
  follower = db.relationship(
    'User',
    secondary = followers,
    primaryjoin = (followers.c.followed_id == id),
    secondaryjoin = (followers.c.follower_id == id),
    backref = db.backref('followed_user', lazy='dynamic'),
    lazy = 'dynamic'
  )
  
  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.password = password
  
  def __repr__(self):
   return (f'<User {self.username}>')
   
  def hash_password(self):
    self.password = generate_password_hash(self.password)
  
  def match_password(self, password=''):
    return check_password_hash(self.password ,password)
  
  def avatar(self, size='80'):
    digest = md5(str(self.email).lower().encode('utf-8')).hexdigest()
    return f'https://gravatar.com/avatar/{digest}?d=identicon&s={size}'
  
  def get_user_by_id(id):
    return User.query.get(int(id))
  
  def update_last_seen(self):
    self.last_seen = datetime.utcnow()
    db.session.commit()
    
  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)
      db.session.commit()
  
  def unfollow (self, user):
    if self.is_following(user):
      self.followed.remove(user)
      db.session.commit()
  
  def is_following(self, user):
    return self.followed.filter(followers.c.followed_id == user.id).count() > 0
  
  def followed_posts(self):
    followed =  Post.query.join(followers,(followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
    own_posts = Post.query.filter(Post.user_id == self.id)
    return followed.union(own_posts).order_by(Post.timestamp.desc()).all()
  
  @login.user_loader
  def get_user(id):
    return User.query.get(int(id))
  
  def own_post(self):
    own_posts = Post.query.filter(Post.user_id == self.id).all()
    return own_posts

  



#  post model class
class Post(db.Model):
  __tablename__ = 'posts'
  id = db.Column(db.Integer, primary_key = True)
  body = db.Column(db.String(300) ,nullable = False)
  title = db.Column(db.String(20), nullable = False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow, index = True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
  def __init__(self, body, title, user_id,):
    self.user_id = user_id
    self.body = body
    self.title = title
    
  def __repr__(self):
    return (f'<Post {self.title} user_id = {self.user_id}>')

