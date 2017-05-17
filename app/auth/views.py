from flask import flash, jsonify, redirect, render_template, request, session, url_for
from . import auth
from .forms import LoginForm, SignUpForm, PasswordReset, UsernameRecover
from .. import db
from ..models import User
from ..email import send_email
from datetime import datetime
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        pass
    elif current_user.confirm(token):
        pass
    else:
        return redirect(url_for('auth.confirmationsent'))
    flash(u'\u2713 Your account has been confirmed!')
    return(redirect(url_for('profile.user_profile', username=current_user.username)))

@auth.route('/confirmationsent/<username>')
@login_required
def confirmationsent(username):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    token=current_user.generate_confirmation_token()
    # send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm',
        # user=username, token=token)
    return render_template('auth/confirmation-sent.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = PasswordReset(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = User.query\
                .filter_by(username=form.username.data)\
                .first()
            if check_user is not None:
                reset_password = User.get_secret_key()
                check_user.password = reset_password
                check_user.invalid_logins = 0
                db.session.add(check_user)
                db.session.commit()
                send_email(check_user.email, 'Reset Your Password', 'auth/email/reset', 
                    user=check_user.username, password=reset_password)
                flash(u'\u2713 Your password has been e-mailed to you')
                return redirect(url_for('auth.login'))
            else:
                flash(u'\u2717 Invalid username')  
        else:
            if 'username' in form.errors:
                flash(u'\u2717 Please enter username')
            if 'email' in form.errors:
                flash(u'\u2717 Please enter email')
            if 'recaptcha' in form.errors:
                flash(u'\u2717 Please validate reCAPTCHA')
        return redirect(url_for('auth.forgot_password'))
    return render_template('auth/forgot-password.html', form=form)

@auth.route('/forgot-username', methods=['GET', 'POST'])
def forgot_username():
    form = UsernameRecover(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = User.query\
                .filter_by(email=form.email.data)\
                .first()
            if check_user is not None:
                send_email(check_user.email, 'Your Username', 'auth/email/username', 
                    user=check_user.username)
                flash(u'\u2713 Your username has been e-mailed to you')
                return redirect(url_for('auth.login'))
            else:
                flash(u'\u2717 Invalid email')
        else:
            if 'email' in form.errors:
                flash(u'\u2717 Please enter email')
            if 'recaptcha' in form.errors:
                flash(u'\u2717 Please validate reCAPTCHA')
        return redirect(url_for('auth.forgot_username'))
    return render_template('auth/forgot-username.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = User.query\
                .filter_by(username=form.username.data)\
                .first()
            if check_user is not None:
                if check_user.invalid_logins >= 5:
                    flash(u'\u2717 Account has been locked. Please reset password')
                    return redirect(url_for('auth.forgot'))
                if check_user.verify_password(form.password.data):
                    login_user(check_user)
                    check_user.invalid_logins = 0
                    check_user.last_login = datetime.utcnow()
                    db.session.add(check_user)
                    db.session.commit()
                    return redirect(request.args.get('next') or url_for('main.index'))
                else:
                    check_user.invalid_logins += 1
                    db.session.add(check_user)
                    db.session.commit()
                    if check_user.invalid_logins >= 5:
                        flash(u'\u2717 Account has been locked. Please reset password')
                        return redirect(url_for('auth.forgot'))
        flash(u'\u2717 Invalid Login')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/-subscribe')
def subscribe_ajax():
    username = request.args.get('username').strip().lower()
    if User.query\
        .filter_by(username=username)\
        .first():
        return jsonify({'exists':True})
    else:
        return jsonify({'exists':False})

@auth.route('/-subscribe-email')
def subscribe_email_ajax():
    email = request.args.get('email').strip().lower()
    if User.query\
        .filter_by(email=email)\
        .first():
        return jsonify({'exists':True})
    else:
        return jsonify({'exists':False})

@auth.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SignUpForm(request.form)
    if request.method == 'POST':
        username_verify = form.username.data.strip().lower()
        email_verify = form.email.data.strip().lower()
        if form.validate():
            user = User(username=username_verify, email=email_verify, 
                password=form.password.data, updates=form.updates.data)
            db.session.add(user)
            try:
                db.session.commit()
                login_user(user)
                return redirect(url_for('auth.confirmationsent', username=username_verify))
            except IntegrityError as e:
                if 'users.username' in str(e):
                    flash(u'\u2717 Username already in use')
                if 'users.email' in str(e):
                    flash(u'\u2717 Email already in use')
                db.session.rollback()
        else:
            if 'username' in form.errors:
                flash(u'\u2717 Username must be between 5 and 12 characters')
            if 'email' in form.errors:
                flash(u'\u2717 Email address is required for registration')
            if 'password' in form.errors:
                if form.password.data != form.password_confirm.data:
                    flash(u'\u2717 Passwords must match')
                if len(form.password.data) < 8:
                    flash(u'\u2717 Password must be at least 8 characters long')
            if 'token' in form.errors:
                flash(u'\u2717 Registration is currently restricted to those with valid tokens')
            if 'recaptcha' in form.errors:
                flash(u'\u2717 Please validate reCAPTCHA')
        return redirect(url_for('auth.subscribe'))
    return render_template('auth/subscribe.html', form=form)

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
    
@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed \
        and not request.endpoint.startswith(('auth', 'main')) \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))