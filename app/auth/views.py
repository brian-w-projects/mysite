from flask import render_template, request, redirect, url_for, session
from . import auth
from .forms import SignUpForm, LoginForm, PasswordReset, UsernameRecover
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users
from .. import db
from ..email import send_email


@auth.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():
        check_user = Users.query.filter_by(username=form.username.data).first()
        if check_user is None:
            user = Users(username=form.username.data, email=form.email.data, password=form.password.data, updates=form.updates.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('auth.confirmationsent', username=user.username, _scheme='https', _external=True))
    return render_template('auth/subscribe.html', form=form)
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        check_user = Users.query.filter_by(username=form.username.data).first()
        if check_user is None:
            form.errors['username'] = 'No Username'
        elif check_user.verify_password(form.password.data):
            login_user(check_user)
            return redirect(request.args.get('next') or url_for('main.index', _scheme='https', _external=True))
        else:
            form.errors['password'] = 'Wrong Password'
    return render_template('auth/login.html', form=form)

@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = PasswordReset(request.form)
    if request.method == 'POST' and form.validate():
        check_user = Users.query.filter_by(username=form.username.data).first()
        if check_user is not None:
            reset_password = Users.get_secret_key()
            check_user.password = reset_password
            db.session.add(check_user)
            db.session.commit()
            send_email(check_user.email, 'Reset Your Password', 'auth/email/reset', user=check_user.username, password=reset_password)
            return redirect(url_for('auth.login', _scheme='https', _external=True))
        else:
            form.errors['username'] = 'Does Not Exist'
    return render_template('auth/forgot.html', form=form)

@auth.route('/forgot_username', methods=['GET', 'POST'])
def forgot_username():
    form = UsernameRecover(request.form)
    if request.method == 'POST' and form.validate():
        check_user = Users.query.filter_by(email=form.email.data).first()
        if check_user is not None:
            send_email(check_user.email, 'Your Username', 'auth/email/username', user=check_user.username)
            return redirect(url_for('auth.login', _scheme='https', _external=True))
        else:
            form.errors['email'] = 'Does Not Exist'
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
    return(redirect(url_for('main.index', _scheme='https', _external=True)))

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
        
