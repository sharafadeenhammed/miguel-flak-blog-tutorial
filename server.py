from os import path, mkdir
from app import app, db
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextAreaField, ValidationError
from models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
from mail import send_password_reset_email


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
  def __init__(self, original_username, *args, **kwargs):
    super(UpdateUserForm, self).__init__(*args, **kwargs)
    self.original_username = original_username

  def validate_username(self, username):
    if username.data != self.original_username:
      user = User.query.filter_by(username=self.username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')
  
# post form 
class PostForm(FlaskForm):
  title = StringField('Title', validators=[validators.DataRequired()])
  body = TextAreaField('Post Body', validators=[validators.DataRequired()])
  submit = SubmitField('Submit post')
  

# reset password form 
class RequestResetPassword(FlaskForm):
  email = StringField('Email', validators=[validators.DataRequired(), validators.Email('Please enter a valid email address')])
  submit = SubmitField('Request Reset Password')
  
class ResetPassword(FlaskForm):
  password = PasswordField('Password', validators=[validators.DataRequired()])
  confirm_password = PasswordField('Confirm Password', validators=[validators.DataRequired(), validators.equal_to('password')])
  submit = SubmitField('Reset Password')

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
  page = request.args.get('page', 1, int)
  posts = current_user.followed_posts().paginate(page = page, per_page = app.config['POST_PER_PAGE'], error_out= False)
  return render_template('index.html', title = 'Welcome', posts = posts)

# explore page
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page = page, per_page = app.config['POST_PER_PAGE'], error_out= False)
    return render_template('index.html', title='Explore', posts=posts)

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
  return render_template('profile.html', title='Profile', user = current_user, posts = current_user.posts)


# update user profile
@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
  form = UpdateUserForm(current_user.username)
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
@login_required
def get_post(id):
  post = Post.query.get_or_404(int(id))
  return render_template('post.html', post=post)

# delete single post
@app.route('/post/<id>', methods = ['POST'])
@login_required
def delete_post(id):
  post = Post.query.get_or_404(int(id))
  db.session.delete(post)
  db.session.commit()
  flash(f'post deleted sucessfully', 'success')
  return redirect(url_for('index'))

# update/edit post
@app.route('/edit_post/<id>')
@login_required
def edit_post(id):
  post = Post.query.get_or_404(int(id))
  return render_template('post.html', post=post)

# fololow user
@app.route('/follow/<id>')
@login_required
def follow(id):
  if(current_user.id == int(id)):
    flash(f'you cannot follow your self', 'error')
    return redirect(f'/user/{id}')
  user = User.query.get(id)
  if(current_user.is_following(user)):
    current_user.unfollow(user)
    flash(f'you are no more following {user.username}', 'success')
    return redirect(f'/user/{user.id}')
  else:
    current_user.follow(user)
    flash(f'you are now following {user.username}', 'success')
    return redirect(f'/user/{user.id}')

# display user profile...
@app.route('/user/<id>')
@login_required
def user_profile(id):
  user = User.query.get(id)
  if user == None:
    flash('this user profile cannot be found, profile may have been deleted or suspended !', 'error')
    return redirect(url_for('index'))
  return render_template('user.html', user=user, posts = user.posts)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RequestResetPassword()
  if form.validate_on_submit():
    user = User.query.filter_by(email = form.email.data).first()
    if user: 
      send_password_reset_email(user)
      print('#send_pssword_request_email(user)', user)
    
    flash('Check your email for instructions on how to reset your password.')
    return redirect(url_for('login'))
  
  return render_template('request_reset_password.html', form = form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  if current_user.is_authenticated: return url_for('index')
  user = User.verify_reset_password_token(token)
  if not token: return redirect(url_for('index'))
  form = ResetPassword()
  if form.validate_on_submit():
    user.password = form.password.data
    user.hash_password()
    db.session.add(user)
    db.session.commit()
    flash('your password has been reset')
    return redirect(url_for('login'))
  return render_template('reset_password.html', form = form)
  



#  log error
if not app.debug and app.config['MAIL_SERVER']:
  auth = None
  if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
  secure = None
  if app.config['MAIL_USE_TLS']:
    secure = ()
  mail_handler = SMTPHandler(
      mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
      fromaddr='no-reply@' + app.config['MAIL_SERVER'],
      toaddrs=app.config['ADMINS'], subject='Microblog Failure',
      credentials=auth, secure=secure
  )
  mail_handler.setLevel(logging.ERROR)
  app.logger.addHandler(mail_handler)
  
  if not path.exists('logs'):
    mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
      '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')


# start server
if __name__ == '__main__':
  app.run(port=8000, load_dotenv=True)
  


  