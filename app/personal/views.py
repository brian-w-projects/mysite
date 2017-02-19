from flask import render_template, request, redirect, url_for, session, abort
from . import personal
from .forms import ChangeForm, PostForm, EditForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Permission
from .. import db
from ..email import send_email
from datetime import datetime

@personal.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    form = ChangeForm(request.form)
    if request.method == 'POST':
        session['updated'] = 'There has been an error updating your profile'
        if form.validate():
            if form.password.data != '':
                if len(form.password.data) >= 8:
                    current_user.password = form.password.data
                else:
                    form.errors['password'] = 'Errors'
            current_user.updates = form.updates.data
            current_user.display=int(form.limit.data)
            current_user.about_me = form.about_me.data
            db.session.add(current_user)
            db.session.commit()
            session['updated'] = 'Your profile has been successfully updated'
        return redirect(url_for('personal.update'))
    form.about_me.data = current_user.about_me
    form.limit.data= str(current_user.display)
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
        if form.validate():
            post = Recommendation(title = form.title.data, public = form.public.data, text = form.text.data, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            form.errors['missing'] = ''
            return redirect(url_for('personal.post', limit=limit))
        else:
            form.errors['missing'] = 'Missing Info'
    return render_template('personal/post.html', form=form, display=display_recs, limit=limit)

@personal.route('/profile')
@personal.route('/profile/<int:id>')
@personal.route('/profile/<int:id>/<int:limit>')
def profile(id=-1, limit=10):
    if id == -1 and current_user.is_authenticated:
        id = current_user.id
    elif id == -1 and not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if limit==10 and current_user.is_authenticated:
        limit=current_user.display
    user = Users.query.filter_by(id=id).first_or_404()
    info = Recommendation.query.filter_by(author_id=user.id).order_by(
        Recommendation.timestamp.desc())
    display_recs = info.limit(limit)
    total = info.count()
    return render_template('personal/profile.html', user=user, display=display_recs, limit=limit, total=total)

@personal.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    display_recs = Recommendation.query.filter_by(id=post_id).first_or_404()
    if display_recs.author_id != current_user.id:
        abort(404)
    form = EditForm(request.form)
    form.errors['missing'] = ''
    if request.method == 'POST':
        if form.validate():
            if form.delete.data == True and form.delete_confirm.data == True:
                db.session.delete(display_recs)
                db.session.commit()
            else:
                display_recs.title = form.title.data
                display_recs.public = form.public.data
                display_recs.timestamp = datetime.utcnow()
                display_recs.text = form.text.data
                db.session.add(display_recs)
                db.session.commit()
            return redirect(url_for('personal.profile'))
        else:
            form.errors['missing'] = 'Error'
    form.title.data = display_recs.title
    form.public.data = display_recs.public
    form.text.data = display_recs.text
    return render_template('personal/edit.html', form=form)