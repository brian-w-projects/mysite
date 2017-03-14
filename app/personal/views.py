from flask import render_template, request, redirect, url_for, session, abort, flash
from . import personal
from .forms import ChangeForm, PostForm, EditForm, CommentEditForm, DeleteForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, Followers
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
            display_comments.verification = 0
            db.session.add(display_comments)
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
                display_comments.verification = 0
                db.session.add(display_comments)
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
                display_recs.verification = form.public.data
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
    form.public.data = display_recs.verification > 0
    form.text.data = display_recs.text
    return render_template('personal/edit.html', form=form)

@personal.route('/_followers')
@login_required
def followers_ajax():
    id = request.args.get('id')
    session['offset'] += session['limit']
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    to_return = user\
        .followed_by\
        .order_by(Followers.timestamp.desc())\
        .offset(session['offset'])\
        .limit(session['limit'])
    return render_template('ajax/followerajax.html', display = to_return, Recommendation=Recommendation)

@personal.route('/followers/<int:id>')
@personal.route('/followers')
def followers(id):
    if current_user.is_authenticated:
        session['limit'] = current_user.display
    else:
        session['limit'] = 10
    session['offset'] = 0
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    to_return = user\
        .followed_by\
        .order_by(Followers.timestamp.desc())\
        .limit(session['limit'])
    return render_template('personal/followers.html', display_names=to_return, 
        user=user, Recommendation=Recommendation)

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

@personal.route('/_following')
def following_ajax():
    id = request.args.get('id')
    session['offset'] += session['limit']
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    to_return = user\
        .following\
        .order_by(Followers.timestamp.desc())\
        .offset(session['offset'])\
        .limit(session['limit'])
    return render_template('ajax/followingajax.html', display_names = to_return, 
        Recommendation=Recommendation, user=user)


@personal.route('/following/<int:id>')
@personal.route('/following')
def following(id):
    if current_user.is_authenticated:
        session['limit'] = current_user.display
    else:
        session['limit'] = 10
    session['offset'] = 0
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    to_return = user\
        .following\
        .order_by(Followers.timestamp.desc())\
        .limit(session['limit'])
    return render_template('personal/following.html', display_names=to_return, user = user, Recommendation=Recommendation)

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
            post = Recommendation(title = form.title.data,
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
    com_count = 0
    rec_count = 0
    if id == -1 and current_user.is_authenticated:
        id = current_user.id
    elif id == -1 and not current_user.is_authenticated:
        return redirect(url_for('auth.login', _scheme='https', _external=True, next='personal/profile'))
    if current_user.is_authenticated:
        limit=current_user.display
        if current_user.is_moderator():
            com_count = Comments.query\
                .filter_by(verification=1)\
                .count()
            rec_count = Recommendation.query\
                .filter_by(verification=1)\
                .count()
    else:
        limit=10
    user = Users.query.filter_by(id=id).first_or_404()
    display_recs = user.posts\
        .order_by(Recommendation.timestamp.desc())\
        .filter_by(made_private=True)
    for rec in display_recs:
        title = rec.title
        if len(rec.title) > 10:
            title = rec.title[:10]
        flash("Rec '" + title + "...' has been made private due to it's content.")
        rec.made_private = False
        db.session.add(rec)
        db.session.commit()
    display_recs = user.posts\
        .order_by(Recommendation.timestamp.desc())\
        .limit(limit)
    display_comments = user.commented_on\
        .filter(Comments.verification != 0)\
        .order_by(Comments.timestamp.desc())\
        .limit(limit)
    return render_template('personal/profile.html', user=user, display=display_recs, 
        d_c=display_comments, id=id, com_count = com_count, rec_count=rec_count)

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