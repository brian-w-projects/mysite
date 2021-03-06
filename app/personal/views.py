from flask import abort, current_app, flash, get_template_attribute, jsonify, redirect, render_template, request, url_for
from . import personal
from .forms import ChangeForm, CommentEditForm, EditForm, PostForm
from .. import db
from ..models import User, Comment, Relationship, Recommendation
from datetime import datetime
from flask_login import current_user, login_required
from flask_moment import _moment
from sqlalchemy import case
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import desc, or_, and_, distinct, func
from ..tasks import prepare_comments

@personal.route('/api')
@login_required
def api():
    if not current_user.api or request.is_xhr:
        current_user.generate_auth_token()
    if request.is_xhr: #ajax request
        return current_user.api
    return render_template('personal/api.html')

@personal.route('/comment-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_edit(id):
    form = CommentEditForm(request.form)
    display_comments = db.session.query(Comment, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Comment.verification>0, Comment.id==id)\
        .first_or_404()
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.verification!=-1, Recommendation.id==display_comments[0].recommendation_id)\
        .first_or_404()
    if current_user.id not in (display_comments[0].user_id, display_comments[0].recommendation.user_id):
        abort(403)
    if request.method == 'POST':
        if form.delete.data:
            display_comments[0].verification = -1
            flash(u'\u2713 Comment has been deleted')
            db.session.add(display_comments[0])
            db.session.commit()
            return redirect(request.args.get('next') or url_for('main.index'))
        elif form.text.data:
            display_comments[0].text = form.text.data
            flash(u'\u2713 Comment updated')
            db.session.add(display_comments[0])
            db.session.commit()
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash(u'\u2717 Check form entry')
            return redirect(url_for('personal.comment_edit', id=id, next=request.args.get('next')))
    form.text.data = display_comments[0].text
    return render_template('personal/comment-edit.html', form=form, rec=display_recs, 
        com=display_comments, next=request.args.get('next'))

@personal.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    form = EditForm(request.form)
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.verification>-1, Recommendation.id==post_id)\
        .first_or_404()
    if display_recs[0].user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            if form.delete.data == True and form.delete_confirm.data == True:
                display_recs[0].verification = -1
                db.session.add(display_recs[0])
                for com in display_recs[0].comment:
                    com.verification = -1
                    db.session.add(com)
                db.session.commit()
                flash(u'\u2713 Your rec has been deleted')
            else:
                display_recs[0].title = form.title.data
                display_recs[0].verification = form.public.data
                display_recs[0].timestamp = datetime.utcnow()
                display_recs[0].text = form.text.data
                display_recs[0].verification = 1 if form.public.data == True else 0
                db.session.add(display_recs[0])
                flash(u'\u2713 Your rec has been edited')
                for com in display_recs[0].comment:
                    com.verification = 1
                    db.session.add(com)
                db.session.commit()
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            if 'title' in form.errors:
                flash(u'\u2717 Recs must contain a title')
            if 'text' in form.errors:
                flash(u'\u2717 Recs must contain text')
            if 'delete' in form.errors:
                flash(u'\u2717 Check both boxes to delete this rec')
            return redirect(url_for('personal.edit', post_id=post_id, next=request.args.get('next')))
    form.title.data = display_recs[0].title
    form.public.data = display_recs[0].verification > 0
    form.text.data = display_recs[0].text
    return render_template('personal/edit.html', form=form, id=post_id,
        next=request.args.get('next'))

@personal.route('/-follow')
@login_required
def follow_ajax():
    id = int(request.args.get('id'))
    if current_user.id == id:
        return jsonify({'added':False}) 
    user = current_user.following\
        .filter_by(following=id)\
        .first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'added':False}) 
    else:
        addition = Relationship(follower=current_user.id, following=id)
        db.session.add(addition)
        db.session.commit()
        return jsonify({'added':True})

@personal.route('/followers/<int:id>')
@personal.route('/followers')
def followers(id=-1):
    if current_user.is_authenticated and id == -1:
        id = current_user.id
    user = User.query.get_or_404(int(id))
    page = int(request.args.get('page', default=1))
    
    last_rec = db.session.query(Recommendation.id, Recommendation.user_id)\
        .filter(Recommendation.verification>0)\
        .filter(Recommendation.user_id.in_([one.follower for one in user.follower]))\
        .order_by(Recommendation.user_id)\
        .order_by(desc(Recommendation.timestamp))\
        .distinct(Recommendation.user_id)\
        .all()
    Rel = aliased(Relationship)
    display_names = db.session.query(User, Recommendation, Relationship)\
        .outerjoin(Recommendation, and_(
            Recommendation.id.in_([each[0] for each in last_rec]),
            Recommendation.user_id == User.id
            )
        )\
        .join(Rel, Rel.follower == User.id)\
        .outerjoin(Relationship, and_(
                Relationship.following == Recommendation.user_id,
                Relationship.follower == current_user.id
                )
        )\
        .filter(User.id.in_([one.follower for one in user.follower]))\
        .order_by(desc(Rel.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    process = [x[1].id for x in display_names.items if x[1]]
    task = prepare_comments.apply_async([process, current_user.id])
    if request.is_xhr: #ajax request
        to_return = get_template_attribute('macros/relationship-macro.html', 'ajax')
        return jsonify({
            'last': display_names.pages in (0, display_names.page),
            'ajax_request': to_return(display_names, _moment, current_user, 
            link=url_for('personal.followers', id=id)),
            'id': task.id
        }) 
    return render_template('personal/followers.html', display=display_names, 
        user=user, id=task.id)

@personal.route('/following/<int:id>')
@personal.route('/following')
def following(id=-1):
    if current_user.is_authenticated and id == -1:
        id = current_user.id
    user = User.query.get_or_404(int(id))
    page = int(request.args.get('page', default=1))
    
    last_rec = db.session.query(Recommendation.id, Recommendation.user_id)\
        .filter(Recommendation.verification>0)\
        .filter(Recommendation.user_id.in_([one.following for one in user.following]))\
        .order_by(Recommendation.user_id)\
        .order_by(desc(Recommendation.timestamp))\
        .distinct(Recommendation.user_id)\
        .all()
    Rel = aliased(Relationship)
    display_names = db.session.query(User, Recommendation, Relationship)\
        .outerjoin(Recommendation, and_(
            Recommendation.id.in_([each[0] for each in last_rec]),
            Recommendation.user_id == User.id
            )
        )\
        .join(Rel, Rel.following == User.id)\
        .outerjoin(Relationship, and_(
                Relationship.following == Recommendation.user_id,
                Relationship.follower == current_user.id
                )
        )\
        .filter(User.id.in_([one.following for one in user.following]))\
        .order_by(desc(Rel.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    process = [x[1].id for x in display_names.items if x[1]]
    task = prepare_comments.apply_async([process, current_user.id])
    if request.is_xhr: #ajax request
        to_return = get_template_attribute('macros/relationship-macro.html', 'ajax')
        return jsonify({
            'last': display_names.pages in (0, display_names.page),
            'ajax_request': to_return(display_names, _moment, current_user, 
                link=url_for('personal.following', id=id)),
            'id': task.id
        }) 
    return render_template('personal/following.html', display=display_names, 
        user = user, id=task.id)

@personal.route('/inspiration')
@login_required
def inspiration():
    page = int(request.args.get('page', default=1))
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.user_id.in_([one.following for one in current_user.following]), 
            Recommendation.verification>0)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    process = [x[0].id for x in display_recs.items]
    task = prepare_comments.apply_async([process, current_user.id])
    if request.is_xhr: #ajax request
        to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
        return jsonify({
            'last': display_recs.pages in (0, display_recs.page),
            'ajax_request': to_return(display_recs, _moment, current_user, 
                link=url_for('personal.inspiration')),
            'id': task.id
        }) 
    return render_template('personal/inspiration.html', display=display_recs, id=task.id)

@personal.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm(request.form)
    if request.method == 'POST':
        if form.validate():
            ver = 1 if form.public.data == True else 0
            post = Recommendation(title = form.title.data,
                text = form.text.data, user_id=current_user.id, verification=ver)
            db.session.add(post)
            db.session.commit()
            flash(u'\u2713 Your rec has been posted!')
        else:
            if 'title' in form.errors:
                flash(u'\u2717 Recs must contain a title')
            if 'text' in form.errors:
                flash(u'\u2717 Recs must contain text')
        return redirect(url_for('personal.post'))
    page = int(request.args.get('page', default=1))
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.verification>0,
            Recommendation.user_id==current_user.id)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    process = [x[0].id for x in display_recs.items]
    task = prepare_comments.apply_async([process, current_user.id])
    if request.is_xhr: #ajax request
        to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
        return jsonify({
            'last': display_recs.pages in (0, display_recs.page),
            'ajax_request': to_return(display_recs, _moment, current_user, 
            link=url_for('personal.post')),
            'id': task.id
        })
    return render_template('personal/post.html', form=form, display=display_recs, id=task.id)

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
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            if 'about_me' in form.errors:
                flash(u'\u2717 About Me may only be 500 characters')
            if 0 < len(form.password.data) < 8:
                flash(u'\u2717 Passwords must be at least 8 characters')
            if form.password.data != form.password_confirm.data:
                flash(u'\u2717 Passwords Must Match')
        return redirect(url_for('personal.update', next=request.args.get('next')))
    form.about_me.data = current_user.about_me
    form.limit.data= str(current_user.display)
    return render_template('personal/update.html', form=form, next=request.args.get('next'))