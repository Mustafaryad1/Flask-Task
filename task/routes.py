import os
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request
from task import app, db, mail, USERS_INFO
from task.forms import LoginForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, logout_user, current_user, login_required
from task.models import User
from flask_mail import Message
from datetime import datetime
import requests


@app.route('/')
@app.route('/home')
def home():
    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successfull', 'success')
            browser = request.user_agent.browser
            version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
            platform = request.user_agent.platform
            user_info = f'''{user.username} accessed from borwser {browser} {version} and platform {platform} '''
            USERS_INFO[user.username].append([datetime.now(), user_info])
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. please check email and password', 'danger')
    return render_template('login.html', form=form, title='login', )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', )
@login_required
def account():
    return render_template('account.html')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request!',
                  sender='noreply@beta.com',
                  recipients=[user.email])
    msg.body = f"""To reset your password visit the following link:{url_for('reset_token',token=token,_external=True)}
    This link is just available for 30 minutes then end!.
    """
    print(msg.body)
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/temperature', methods=['POST'])
def temperature():
    zipcode = request.form['zip'] # try us zip codes
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?zip=' + zipcode + ',us&appid=7da4f277c2f075ee04154bc5b3e9ba2e')
    json_object = r.json()
    temp_k = float(json_object['main']['temp'])
    temp_f = (temp_k - 273.15) * 1.8 + 32
    return render_template('temperature.html', temp=temp_f)


@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            flash('file uploaded', 'success')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('home'))
    else:
        return render_template('upload_file.html')
