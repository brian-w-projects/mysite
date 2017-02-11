from flask import render_template, request, redirect, url_for, session
from . import personal
from .forms import ChangeForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users
from .. import db
from ..email import send_email

@personal.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    form = ChangeForm(request.form)
    form.errors['updated'] = ''
    if request.method == 'POST' and form.validate():
        if form.password.data != '':
            if len(form.password.data) >= 8:
                current_user.password = form.password.data
            else:
                form.errors['password'] = 'Errors'
        current_user.updates = form.updates.data
        db.session.add(current_user)
        db.session.commit()
        form.errors['updated'] = 'Your profile has been successfully updated'
    return render_template('personal/update.html', form=form)