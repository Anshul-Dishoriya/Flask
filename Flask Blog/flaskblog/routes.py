from flask import  url_for ,redirect , render_template ,flash ,get_flashed_messages ,request ,abort
from flaskblog import app , db , bcrypt , mail
from flaskblog.forms import LoginForm, RegistrationForm ,UpdateAccountForm ,PostForm ,RequestResetForm , ResetPasswordForm
from flaskblog.models import User , Post 
from flask_login import login_user ,current_user ,logout_user,login_required
import  secrets
import os # to save the image file and to change  name of image file
from PIL import Image # To Resize Our Image
from flask_mail import Message



# Home Route
@app.route('/', methods=['GET'])
def home():
    global page
    page = request.args.get('page' , 1 ,type=int)
    posts = Post.query.order_by(Post.date_posted.desc())
    posts = posts.paginate(page=page , per_page=5)
    return render_template('home.html' ,posts=posts)


# Regidter Route
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form  = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data , email = form.email.data , password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been Created ! You are now able to Log In!' ,'success')
        return redirect(url_for('login'))
    return render_template('register.html' ,title='Sign Up' , form=form )

# Login Route
@app.route('/login', methods=['GET','POST'])
def login():
    form  = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user , remember=form.rememberme.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsucessful. Please check Email and Password!','danger')
    return render_template('login.html' ,title='Log In' ,form=form )

# About Route
@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html' ,title='About Us')
    # return redirect(url_for('about'))
    

# Logout Route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
 


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    # to know or save the extension we are using os.path.splitext function wihich will return the filename and extension. Here we do not require filename so we are storing it into a '_'(underscore) variable  
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path , 'static/profile_pics' ,picture_file_name)
    # Resizing Our Profile Picture
    picture_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(picture_size)
    i.save(picture_path)
    return picture_file_name
# Account Route
@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form  = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file_name = save_picture(form.picture.data)
            current_user.image_file = picture_file_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been  Updated!' ,'success')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',title='Account' ,
                            image_file=image_file , form=form)



@app.route('/post/new' , methods=['GET', 'POST'])
# @login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data , content = form.content.data , author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been Created!' , 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='Add Post' , form=form ,legend='New Post')


@app.route('/post/<int:post_id>' , methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html' ,title=post.title , post=post)

@app.route('/post/<int:post_id>/update' , methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post  = Post.query.get_or_404(post_id)
    if post.author.username != current_user.username:
        abort(403)
    form  = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!' ,'success')
        return redirect(url_for('post' , post_id = post.id))
    elif request.method=="GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',title='Update Post' , form=form , legend='Update Post')


@app.route('/post/<int:post_id>/delete' , methods=['POST'])
@login_required
def delete_post(post_id):
    post  = Post.query.get_or_404(post_id)
    if post.author.username != current_user.username:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been Deleted!' , 'success')
    return redirect(url_for('home',page = page))

@app.route('/user/<string:username>', methods=['GET'])
def user_post(username):
    page = request.args.get('page' , 1 ,type=int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc())
    posts = posts.paginate(page=page , per_page=5)
    return render_template('user_post.html' ,posts=posts , user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Reset Password Request',
        sender='noreply@demo.com',
        recipients=[user.email])
    msg.body = f'''To reset your Password , Visit the following link : {url_for('reset_token' , token = token , _external = True)}

If you did not made this request then simply ignore this Email and no changs will be Made.
'''
    mail.send(msg)



@app.route('/reset_password', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An Email has been sent with instruction to reset your password' , 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html' , title='Reset Password' , form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired token!' , 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your Password has been Updated! You are now able to Log In!' ,'success')
        return redirect(url_for('login'))
    return render_template( 'reset_token.html' , title='Reset Password' , form =form )