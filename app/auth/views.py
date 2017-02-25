from flask import render_template, request, redirect, url_for, session, flash
from . import auth
from .forms import SignUpForm, LoginForm, PasswordReset, UsernameRecover
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users
from .. import db
from datetime import datetime
from ..email import send_email


@auth.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SignUpForm(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = Users.query.filter_by(username=form.username.data).first()
            if check_user is None:
                user = Users(username=form.username.data, email=form.email.data, password=form.password.data, updates=form.updates.data)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('auth.confirmationsent', username=user.username, _scheme='https', _external=True))
            else:
                flash(u'\u2717 Username already in use')
        else:
            if 'username' in form.errors:
                flash(u'\u2717 Username must be at least 4 characters')
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
        return redirect(url_for('auth.subscribe', _scheme='https', _external=True))
    return render_template('auth/subscribe.html', form=form)
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = Users.query.filter_by(username=form.username.data).first()
            if check_user.invalid_logins >= 5:
                flash(u'\u2717 Account has been locked. Please reset password')
                return redirect(url_for('auth.forgot', _scheme='https', _external=True))
            if check_user is not None and check_user.verify_password(form.password.data):
                login_user(check_user)
                check_user.invalid_logins = 0
                check_user.last_login = datetime.utcnow()
                db.session.add(check_user)
                db.session.commit()
                return redirect(request.args.get('next') or url_for('main.index', _scheme='https', _external=True))
            elif check_user is not None:
                check_user.invalid_logins += 1
                db.session.add(check_user)
                db.session.commit()
                if check_user.invalid_logins >= 5:
                    flash(u'\u2717 Account has been locked. Please reset password')
                    return redirect(url_for('auth.forgot', _scheme='https', _external=True))
        flash(u'\u2717 Invalid Login')
        return redirect(url_for('auth.login', _scheme='https', _external=True))
    return render_template('auth/login.html', form=form)

@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = PasswordReset(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = Users.query.filter_by(username=form.username.data).first()
            if check_user is not None:
                reset_password = Users.get_secret_key()
                check_user.password = reset_password
                check_user.invalid_logins = 0
                db.session.add(check_user)
                db.session.commit()
                send_email(check_user.email, 'Reset Your Password', 'auth/email/reset', user=check_user.username, password=reset_password)
                flash(u'\u2713 Your password has been e-mailed to you')
                return redirect(url_for('auth.login', _scheme='https', _external=True))
            else:
                flash(u'\u2717 Invalid username')  
        else:
            if 'username' in form.errors:
                flash(u'\u2717 Please enter username')
            if 'email' in form.errors:
                flash(u'\u2717 Please enter email')
            if 'recaptcha' in form.errors:
                flash(u'\u2717 Please validate reCAPTCHA')
        return redirect(url_for('auth.forgot', _scheme='https', _external=True))
    return render_template('auth/forgot.html', form=form)

@auth.route('/forgot_username', methods=['GET', 'POST'])
def forgot_username():
    form = UsernameRecover(request.form)
    if request.method == 'POST':
        if form.validate():
            check_user = Users.query.filter_by(email=form.email.data).first()
            if check_user is not None:
                send_email(check_user.email, 'Your Username', 'auth/email/username', user=check_user.username)
                flash(u'\u2713 Your username has been e-mailed to you')
                return redirect(url_for('auth.login', _scheme='https', _external=True))
            else:
                flash(u'\u2717 Invalid email')
        else:
            if 'email' in form.errors:
                flash(u'\u2717 Please enter email')
            if 'recaptcha' in form.errors:
                flash(u'\u2717 Please validate reCAPTCHA')
        return redirect(url_for('auth.forgot_username', _scheme='https', _external=True))
    return render_template('auth/forgot_username.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index', _scheme='https', _external=True))

@auth.route('/confirmationsent/<username>')
@login_required
def confirmationsent(username):
    if current_user.confirmed:
        return redirect(url_for('main.index', _scheme='https', _external=True))
    token=current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=username, token=token)
    return render_template('auth/confirmationsent.html')

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        pass
    elif current_user.confirm(token):
        pass
    else:
        return redirect(url_for('auth.confirmationsent', _scheme='https', _external=True))
    flash(u'\u2713 Your account has been confirmed!')
    return(redirect(url_for('personal.profile', _scheme='https', _external=True)))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index', _scheme='https', _external=True))
    return render_template('auth/unconfirmed.html')
    
@auth.before_app_request
def before_request():
    if  current_user.is_authenticated  and not current_user.confirmed \
    and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed', _scheme='https', _external=True))
        
