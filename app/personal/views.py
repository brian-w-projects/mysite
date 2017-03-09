from flask import render_template, request, redirect, url_for, session, abort, flash
from . import personal
from .forms import ChangeForm, PostForm, EditForm, CommentEditForm, DeleteForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Permission, Comments, Followers
from .. import db
from ..email import send_email
from datetime import datetime
import json

@personal.route('/commentdelete/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_delete(id):
    form = DeleteForm(request.form)
    display_comments = Comments.query\
        .filter_by(id=id)\
        .first_or_404()
    display_recs = Recommendation.query\
        .filter_by(id=display_comments.posted_on)\
        .first_or_404()
    if display_recs.author_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            db.session.delete(display_comments)
            db.session.commit()
            flash(u'\u2713 Comment has been deleted')
            return redirect(url_for('main.highlight', id=display_recs.id, _scheme='https', _external=True))
        else:
            flash(u'\u2717 You must confirm deletion')
            return redirect(url_for('personal.comment_delete', id=id, _scheme='https', _external=True))
        return redirect(url_for('personal.comment_delete', id=id, _scheme='https', _external=True))
    return render_template('personal/commentdelete.html', form=form, rec=display_recs, com=display_comments)

@personal.route('/commentedit/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_edit(id):
    form = CommentEditForm(request.form)
    display_comments = Comments.query\
        .filter_by(id=id)\
        .first_or_404()
    display_recs = Recommendation.query\
        .filter_by(id=display_comments.posted_on)\
        .first_or_404()
    if display_comments.comment_by != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            if form.delete.data:
                db.session.delete(display_comments)
                db.session.commit()
                flash(u'\u2713 Comment deleted')
                return redirect(url_for('main.highlight', id=display_recs.id, _scheme='https', _external=True))
            else:
                display_comments.comment = form.text.data
                db.session.add(display_comments)
                db.session.commit()
                flash(u'\u2713 Comment updated')
                return redirect(url_for('main.highlight', id=display_recs.id, _scheme='https', _external=True))
        else:
            flash(u'\u2717 Comment must contain text')
            return redirect(url_for('personal.comment_edit', id=id, _scheme='https', _external=True))
    form.text.data = display_comments.comment
    return render_template('personal/commentedit.html', form=form, rec=display_recs, com=display_comments)

@personal.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    form = EditForm(request.form)
    display_recs = Recommendation.query.filter_by(id=post_id).first_or_404()
    if display_recs.author_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            if form.delete.data == True and form.delete_confirm.data == True:
                db.session.delete(display_recs)
                db.session.commit()
                flash(u'\u2713 Your rec has been deleted')
                return redirect(url_for('personal.profile', _scheme='https', _external=True))
            else:
                display_recs.title = form.title.data
                display_recs.public = form.public.data
                display_recs.timestamp = datetime.utcnow()
                display_recs.text = form.text.data
                display_recs.verification = form.public.data
                db.session.add(display_recs)
                db.session.commit()
                flash(u'\u2713 Your rec has been edited')
        else:
            if 'title' in form.errors:
                flash(u'\u2717 Recs must contain a title')
            if 'text' in form.errors:
                flash(u'\u2717 Recs must contain text')
            if 'delete' in form.errors:
                flash(u'\u2717 Check both boxes to delete this rec')
        return redirect(url_for('personal.edit', post_id=post_id, _scheme='https', _external=True))
    form.title.data = display_recs.title
    form.public.data = display_recs.public
    form.text.data = display_recs.text
    return render_template('personal/edit.html', form=form)

@personal.route('/followers')
@login_required
def followers():
    to_return = current_user.followed_by.order_by(Followers.timestamp.desc())
    return render_template('personal/followers.html', display_names=to_return)

@personal.route('/_follow')
@login_required
def follow_ajax():
    id = request.args.get('id')
    if request.args.get('follow') == 'true':
        addition = Followers(follower=current_user.id, following=id)
        db.session.add(addition)
        db.session.commit()
        return json.dumps({'added':True}), 200, {'ContentType':'application/json'} 
    else:
        to_delete = current_user.following.filter_by(following=id).first()
        db.session.delete(to_delete)
        db.session.commit()
        return json.dumps({'added':False}), 200, {'ContentType':'application/json'} 

@personal.route('/following')
@login_required
def following():
    to_return = current_user.following.order_by(Followers.timestamp.desc())
    return render_template('personal/following.html', display_names=to_return)

@personal.route('/_inspiration')
@login_required
def inspiration_ajax():
    session['offset'] += current_user.display
    following = [x.who.id for x in current_user.following]
    display_recs = Recommendation.query\
        .filter(Recommendation.author_id.in_(following))\
        .order_by(Recommendation.timestamp.desc())\
        .offset(session['offset'])\
        .limit(current_user.display)
    return render_template('ajax/postajax.html', display = display_recs)   

@personal.route('/inspiration')
@login_required
def inspiration():
    session['offset'] = 0
    following = [x.who.id for x in current_user.following]
    display_recs = Recommendation.query\
        .filter(Recommendation.author_id.in_(following))\
        .order_by(Recommendation.timestamp.desc())\
        .limit(current_user.display)
    return render_template('personal/inspiration.html', display=display_recs)

@personal.route('/_post')
@login_required
def post_ajax():
    session['offset'] += current_user.display
    display_recs = Recommendation.query\
        .filter_by(author_id=current_user.id)\
        .order_by(Recommendation.timestamp.desc())\
        .offset(session['offset'])\
        .limit(current_user.display)
    return render_template('ajax/postajax.html', display = display_recs)

@personal.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    session['offset'] = 0
    form = PostForm(request.form)
    if request.method == 'POST':
        if form.validate():
            ver = form.public.data
            post = Recommendation(title = form.title.data, public = form.public.data, 
                text = form.text.data, author_id=current_user.id, verification=ver)
            db.session.add(post)
            db.session.commit()
            flash(u'\u2713 Your rec has been posted!')
        else:
            if 'title' in form.errors:
                flash(u'\u2717 Recs must contain a title')
            if 'text' in form.errors:
                flash(u'\u2717 Recs must contain text')
        return redirect(url_for('personal.post', _scheme='https', _external=True))
    display_recs = Recommendation.query\
        .filter_by(author_id=current_user.id)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(current_user.display)
    return render_template('personal/post.html', form=form, display=display_recs)

@personal.route('/_profileCom')
def profileCom_ajax():
    id = request.args.get('id')
    if current_user.is_authenticated:
        limit = current_user.display
    else:
        limit = 10
    session['offsetCom'] += limit
    display_comments = Comments.query\
        .filter_by(comment_by=id)\
        .order_by(Comments.timestamp.desc())\
        .offset(session['offsetCom'])\
        .limit(limit)
    return render_template('ajax/commentajax.html', d_c = display_comments)

@personal.route('/_profile')
def profile_ajax():
    id = request.args.get('id')
    if current_user.is_authenticated:
        limit = current_user.display
    else:
        limit = 10
    session['offset'] += limit
    display_recs = Recommendation.query\
        .filter_by(author_id=id)\
        .order_by(Recommendation.timestamp.desc())\
        .offset(session['offset'])\
        .limit(limit)
    return render_template('ajax/postajax.html', display = display_recs)

@personal.route('/profile')
@personal.route('/profile/<int:id>')
def profile(id=-1):
    session['offset'] = 0
    session['offsetCom'] = 0
    if id == -1 and current_user.is_authenticated:
        id = current_user.id
    elif id == -1 and not current_user.is_authenticated:
        return redirect(url_for('auth.login', _scheme='https', _external=True, next='personal/profile'))
    if current_user.is_authenticated:
        limit=current_user.display
    else:
        limit=10
    user = Users.query.filter_by(id=id).first_or_404()
    display_recs = user.posts.order_by(Recommendation.timestamp.desc()).limit(limit)
    display_comments = user.commented_on.order_by(Comments.timestamp.desc()).limit(limit)
    return render_template('personal/profile.html', user=user, display=display_recs, d_c=display_comments, id=id)

@personal.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    form = ChangeForm(request.form)
    if request.method == 'POST':
        if form.validate():
            if form.password.data != '':
                current_user.password = form.password.data
            current_user.updates = form.updates.data
            current_user.display=int(form.limit.data)
            current_user.about_me = form.about_me.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'\u2713 Your profile has been successfully updated')
        else:
            if 'about_me' in form.errors:
                flash(u'\u2717 About Me may only be 500 characters')
            if 0 < len(form.password.data) < 8:
                flash(u'\u2717 Passwords must be at least 8 characters')
            if form.password.data != form.password_confirm.data:
                flash(u'\u2717 Passwords Must Match')
        return redirect(url_for('personal.update', _scheme='https', _external=True))
    form.about_me.data = current_user.about_me
    form.limit.data= str(current_user.display)
    return render_template('personal/update.html', form=form)