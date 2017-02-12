from flask import render_template, request, redirect, url_for, session
from . import personal
from .forms import ChangeForm, PostForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Permission
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
        if form.limit.data != '':
            current_user.display=int(form.limit.data)
        if form.about_me.data != '':
            current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        form.errors['updated'] = 'Your profile has been successfully updated'
        return redirect(url_for('personal.update'))
    form.about_me.data = current_user.about_me
    return render_template('personal/update.html', form=form)
    
@personal.route('/post', methods=['GET', 'POST'])
@personal.route('/post/<int:limit>', methods=['GET', 'POST'])
@login_required
def post(limit=10):
    form = PostForm(request.form)
    form.errors['missing'] = ''
    display_recs = Recommendation.query.filter_by(author_id=current_user.id).order_by(
        Recommendation.timestamp.desc()).limit(limit)
    if request.method == 'POST':
        if form.validate() and current_user.can(Permission.WRITE_ARTICLES):
            post = Recommendation(title = form.title.data, public = form.public.data, text = form.text.data, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            form.errors['missing'] = ''
            return redirect(url_for('personal.post', limit=limit))
        else:
            form.errors['missing'] = 'Missing Info'
    return render_template('personal/post.html', form=form, display=display_recs, limit=limit)
        