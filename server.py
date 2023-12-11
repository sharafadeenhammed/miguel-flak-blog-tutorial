from os import path
from app import app, db
from flask import render_template, request, flash, redirect, url_for, session
from config import Config
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextAreaField
from models import User, Post, followers
from flask_login import current_user, login_user, logout_user, login_required

# login form 
class LoginForm(FlaskForm):
  username = StringField('Username', validators=[validators.DataRequired()])
  password = PasswordField('Password', description='password', validators=[validators.DataRequired(), validators.Length(min=8, message='Enter at leaast 8 characters')])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')

# register form
class RegisterForm(FlaskForm):
  username = StringField('Username', validators=[validators.DataRequired()])
  email = StringField('Email', validators=[validators.DataRequired(), validators.Email('Please enter a valid email address')])
  password = PasswordField('Password', description='password', validators=[validators.DataRequired(), validators.Length(min=8, message='Enter at leaast 8 characters'), validators.EqualTo('confirm', 'passwords does not match')])
  confirm = PasswordField('Confirm Password', description='confirm password', validators=[validators.DataRequired(), validators.Length(min=8, message='Enter at leaast 8 characters')])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign Up')
  

# update user form
class UpdateUserForm(FlaskForm):
  username = StringField('Username', validators=[validators.DataRequired()])
  about = TextAreaField('About Me', validators=[validators.Length( max=150)])
  submit = SubmitField('Submit')
  
# post form 
class PostForm(FlaskForm):
  title = StringField('Title', validators=[validators.DataRequired()])
  body = TextAreaField('Post Body', validators=[validators.DataRequired()])
  submit = SubmitField('Submit post')

basedir = path.abspath(path.dirname(__file__))
static_folder = path.join(basedir, 'templates', 'styles')


# before response middleware
@app.before_request
def validate():
  if current_user.is_authenticated:
    current_user.update_last_seen()

# home route
@app.route("/")
# @app.route('/index')
@login_required
def index():
  post = current_user.followed_posts()
  return render_template('index.html', title = 'Welocome', posts = post)

# login route
@app.route("/login/", methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
 
  form = LoginForm()
  
  # validate login
  if form.validate_on_submit():
    user = User.query.filter_by(username = form.username.data).first()
    
    # validate user credentials
    if user == None or user.match_password(form.password.data) == False:
      flash('Invalid login credentials','error')
      return redirect(url_for('login'))
    
    next_url = request.args.get('next')
    if(next_url):
      print(f'next url={next_url}')
      flash(f'welcome {form.username.data}, you are logged in succesfully ', category='success')
      login_user(user, remember=form.remember_me.data)
      return redirect(next_url)
    flash(f'welcome {form.username.data} ', category='success')
    login_user(user, remember=form.remember_me.data)
    return redirect(url_for('index'))
      
  return render_template('login.html', title='Sign In', form = form )
 
# logout route 
@app.route('/logout/', methods=['GET', 'POST'])
def logout():
  logout_user()
  return redirect(url_for('login'))

# register route
@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegisterForm()
  
  if form.validate_on_submit():
    user = User(form.username.data, form.email.data, form.password.data)
    user.hash_password()
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=form.remember_me.data)
    flash(f'welcome {user.username} your account is registered succesfully', 'success')
    return redirect(url_for('index'))
  return render_template('register.html', title='Sign Up', form = form)

#  logged in user profile route
@app.route('/profile')
@login_required
def profile():
  return render_template('profile.html', title='Profile', user = current_user)


# update user profile
@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
  form = UpdateUserForm()
  if form.validate_on_submit():
    current_user.about_me = form.about.data
    current_user.username = form.username.data
    db.session.commit()
    flash('profile updated', 'success')
    return redirect(url_for('profile'))
  return render_template('edit_profile.html', title='Edit Profile ', form = form)

# add new post
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
  form = PostForm()
  if form.validate_on_submit():
    post = Post(form.body.data, form.title.data, current_user.id)
    db.session.add(post)
    db.session.commit()
    flash('post added', 'success')
    return redirect(url_for('index'))
  return render_template('add_post.html', title = 'Add New Post', form = form)

# get single post
@app.route('/post/<id>')
def get_post(id):
  post = Post.query.get_or_404(int(id))
  return render_template('post.html', post=post)

# delete single post
@app.route('/post/<id>', methods = ['POST'])
def delete_post(id):
  post = Post.query.get_or_404(int(id))
  db.session.delete(post)
  db.session.commit()
  flash(f'post deleted sucessfully', 'success')
  return redirect(url_for('index'))

# update/edit post
@app.route('/edit_post/<id>')
def edit_post(id):
  post = Post.query.get_or_404(int(id))
  return render_template('post.html', post=post)



# start server
if __name__ == '__main__':
  app.run(port=8000, debug=True, load_dotenv=True)
  