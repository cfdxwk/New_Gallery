import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, AlbumForm, PostForm,UpdateAlbumForm
from flaskblog.models import User, Post, Album, LikePost, LikeAlbum
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home1():
    if current_user.is_authenticated:
        albums = Album.query.all()
        liked_albums_id = LikeAlbum.query.filter_by(user_id=current_user.id,is_liked=True).all()
        liked_list=[]
        for alb in liked_albums_id:
            liked_list.append(alb.album_id)
        #albums = current_user.albums
        return render_template('home.html', albums=albums, current_user=current_user, user_id=current_user.id,liked_albums=liked_list)
    else:
        return render_template('home1.html')

@app.route("/user/<int:user_id>")
def user(user_id):
    u = User.query.get_or_404(user_id)
    albums = Album.query.filter_by(user_id=user_id).all()
    #albums = current_user.albums
    return render_template('home.html', albums=albums,  current_user=current_user, user_id=user_id)

@app.route("/album/<int:album_id>")
def album(album_id):
    a = Album.query.get_or_404(album_id)
    u_id = a.user_id
    posts = Post.query.filter_by(album_id=album_id).all()
    liked_posts_id = LikePost.query.filter_by(user_id=current_user.id,is_liked=True).all()
    liked_list=[]
    for post in liked_posts_id:
        liked_list.append(post.post_id)
        
    return render_template('all_posts.html', posts=posts, current_user=current_user, album_id=album_id, user_id=u_id,album_name=a.album_name,liked_posts=liked_list)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f"user/{current_user.id}"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, firstname=form.firstname.data,lastname=form.lastname.data, 
            gender=form.gender.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.user', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('.user', user_id=current_user.id)) 
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home1'))


def save_picture(form_picture,folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/'+folder, picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data,'profile_pics')
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.gender = form.gender.data
        current_user.email = form.email.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password=hashed_password
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.gender.data = current_user.gender
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/album/new", methods=['GET', 'POST'])
@login_required
def new_album():
    form = AlbumForm()
    if form.validate_on_submit():
        if form.cover_pic.data:
            picture_file = save_picture(form.cover_pic.data,'album_cover')
        else:
            picture_file='default.jpeg'
        if form.is_private.data:
            private=1
        else:
            private=0
        album= Album(album_name=form.album_name.data, is_private=private, author=current_user,cover_pic=picture_file,likes=0)
        db.session.add(album)
        db.session.commit()
        flash('Your album has been created!', 'success')
        next_page = request.args.get('next')
        return redirect(url_for('.user', user_id=current_user.id)) if next_page else redirect(url_for('home1'))
    return render_template('create_album.html', title='New Album', form=form)

@app.route("/update_album/<int:album_id>",methods=['GET','POST'])
@login_required
def update_album(album_id):
    form=UpdateAlbumForm()

    if request.method=='GET':
        a = Album.query.filter_by(id=album_id,user_id=current_user.id).all()
        if len(a)==0:
            flash('Album not found', 'danger')
        else:
            form.album_name.data=a[0].album_name
            form.cover_pic.data=a[0].cover_pic
            form.is_private.data=a[0].is_private
        return render_template('update_album.html', title='Update Album', form=form)

    elif request.method=='POST':
        if form.is_private.data:
            private=1
        else:
            private=0

        if form.cover_pic.data:
            picture_file = save_picture(form.cover_pic.data,'album_cover')
            album= Album.query.filter_by(id=album_id).update(album_name=form.album_name.data, is_private=private,cover_pic=picture_file)
        
        else:
            album= Album.query.filter_by(id=album_id).update(dict(album_name=form.album_name.data, is_private=private))
        db.session.commit()
        flash('Your album has been updated!', 'success')
        return redirect(url_for('.home1'))

@app.route("/delete_album/<int:album_id>",methods=['GET'])
@login_required
def delete_album(album_id):
    a = Album.query.filter_by(id=album_id,user_id=current_user.id).all()
    if len(a)==0:
        flash('Album not found', 'danger')
    else:
        Post.query.filter_by(album_id=album_id).delete()
        Album.query.filter_by(id=album_id).delete()
        db.session.commit()
        flash('Your album has been deleted!', 'success')
    return redirect(url_for('.home1'))

@app.route("/post/new/<int:album_id>", methods=['GET', 'POST'])
@login_required
def new_post(album_id):
    form = PostForm()
    #save the picture 
    if form.validate_on_submit():
        image_file = save_picture(form.image_file.data,'all_posts')
        if form.is_private.data:
            private=1
        else:
            private=0
        post = Post(title= form.title.data, is_private= private, image_file= image_file, user_id=current_user.id, album_id=album_id,likes=0)
        db.session.add(post)
        db.session.commit()
        flash('Your Photo has been uploaded', 'success')
        return redirect(url_for('.album', album_id=album_id))
    return render_template('create_post.html', title='New Post', form=form)


@app.route("/delete_post/<int:post_id>",methods=['GET'])
@login_required
def delete_post(post_id):
    p = Post.query.filter_by(id=post_id, user_id=current_user.id).all()
    if len(p)==0:
        flash('Post not found', 'danger')
    else:
        Post.query.filter_by(id=post_id).delete()
        db.session.commit()
        flash('Your Post has been deleted!', 'success')
    return redirect(request.referrer)


#here user_id denotes the current user who is currently trying to like or dislike the post
@app.route("/like_post/<int:post_id>/")
@login_required
def like_post(post_id):
    cur_entry = LikePost.query.filter_by(post_id=post_id, user_id=current_user.id).all()
    p = Post.query.filter_by(id = post_id).first()
    if len(cur_entry)==0:
        obj = LikePost(is_liked=True, post_id=post_id, user_id=current_user.id)
        db.session.add(obj)
        p.likes= p.likes+1
        db.session.commit()
        flash('Post liked successfully!', 'success')

    else:
        # if the post is already liked, dislike it  by deleting the entry from database
        LikePost.query.filter_by(post_id=post_id ,user_id=current_user.id).delete()
        db.session.commit()
        p.likes= p.likes-1
        db.session.commit()

    return redirect(request.referrer)

@app.route("/like_album/<int:album_id>/")
@login_required
def like_album(album_id):
    cur_entry = LikeAlbum.query.filter_by(album_id=album_id, user_id=current_user.id).all()
    a = Album.query.filter_by(id = album_id).first()
    if len(cur_entry)==0:
        obj = LikeAlbum(is_liked=True, album_id=album_id, user_id=current_user.id)
        db.session.add(obj)
        a.likes= a.likes+1
        db.session.commit()
        flash('Album liked successfully!', 'success')

    else:
        # if the post is already liked, dislike it by deleting the entry from database
        LikeAlbum.query.filter_by(album_id=album_id ,user_id=current_user.id).delete()
        db.session.commit()
        a.likes= a.likes-1
        db.session.commit()
        #a.likes--   
    return redirect(url_for('.home1'))






