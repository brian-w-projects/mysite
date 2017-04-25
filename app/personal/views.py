from flask import abort, current_app, flash, get_template_attribute, jsonify, redirect, render_template, request, url_for
from . import personal
from .forms import ChangeForm, CommentEditForm, EditForm, PostForm
from .. import db
from ..models import User, Comment, Relationship, Recommendation
from datetime import datetime
from flask_login import current_user, login_required
from flask_moment import _moment
from sqlalchemy import case
from sqlalchemy.sql.expression import desc

@personal.route('/-api')
@login_required
def api_ajax():
    current_user.generate_auth_token()
    return current_user.api

@personal.route('/api')
@login_required
def api():
    if not current_user.api:
        current_user.generate_auth_token()
    return render_template('personal/api.html')

@personal.route('/comment-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_edit(id):
    form = CommentEditForm(request.form)
    display_comments = Comment.query\
        .filter(Comment.verification>0, Comment.id==id)\
        .first_or_404()
    display_recs = display_comments.recommendation
    if current_user.id not in (display_comments.user_id, display_comments.recommendation.user_id):
        abort(403)
    if request.method == 'POST':
        if form.delete.data:
            display_comments.verification = -1
            flash(u'\u2713 Comment has been deleted')
            db.session.add(display_comments)
            db.session.commit()
            return redirect(request.args.get('next') or url_for('main.index'))
        elif form.text.data:
            display_comments.text = form.text.data
            flash(u'\u2713 Comment updated')
            db.session.add(display_comments)
            db.session.commit()
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash(u'\u2717 Check form entry')
            return redirect(url_for('personal.comment_edit', id=id, next=request.args.get('next')))
    form.text.data = display_comments.text
    return render_template('personal/comment-edit.html', form=form, rec=display_recs, 
        com=display_comments, next=request.args.get('next'))

@personal.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    form = EditForm(request.form)
    display_recs = Recommendation.query\
        .filter(Recommendation.verification>-1, Recommendation.id==post_id)\
        .first_or_404()
    if display_recs.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            if form.delete.data == True and form.delete_confirm.data == True:
                display_recs.verification = -1
                db.session.add(display_recs)
                for com in display_recs.comment:
                    com.verification = -1
                    db.session.add(com)
                db.session.commit()
                flash(u'\u2713 Your rec has been deleted')
            else:
                display_recs.title = form.title.data
                display_recs.verification = form.public.data
                display_recs.timestamp = datetime.utcnow()
                display_recs.text = form.text.data
                display_recs.verification = form.public.data
                db.session.add(display_recs)
                flash(u'\u2713 Your rec has been edited')
                for com in display_recs.comment:
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
    form.title.data = display_recs.title
    form.public.data = display_recs.verification > 0
    form.text.data = display_recs.text
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

@personal.route('/-followers/<int:id>')
def followers_ajax(id):
    page = int(request.args.get('page'))
    user = User.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = db.session.query(User.id, Recommendation, Relationship)\
        .join(Recommendation)\
        .join(Relationship, Relationship.follower == User.id)\
        .filter(User.id.in_([one.follower for one in user.follower]), 
            Recommendation.verification>0)\
        .order_by(desc(Relationship.timestamp))\
        .group_by(User.id)\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/followed-macro.html', 'ajax')
    return jsonify({
        'last': display_names.pages in (0, display_names.page),
        'ajax_request': to_return(display_names, _moment, current_user, 
            link=url_for('personal.followers', id=id))}) 

@personal.route('/followers/<int:id>')
@personal.route('/followers')
def followers(id=-1):
    if current_user.is_authenticated and id == -1:
        id = current_user.id
    user = User.query\
        .filter_by(id=id)\
        .first_or_404()
    
    case_check = case([(Recommendation.user_id.in_([one.follower for one in user.follower]) & Recommendation.verification>0, Recommendation.id)], else_=None)
    display_names = db.session.query(User, case_check, Recommendation)\
        .outerjoin(Recommendation)\
        .filter(User.id.in_([one.follower for one in user.follower]))\
        .paginate(1, per_page=current_user.display, error_out=False)
    # display_names = db.session.query(User, Recommendation)\
    #     .join(Relationship, Relationship.follower == User.id)\
    #     .filter(User.id.in_([one.follower for one in user.follower]))\
    #     .order_by(desc(Relationship.timestamp))\
    #     .group_by(User.id)\
    #     .paginate(1, per_page=current_user.display, error_out=False)
    for x in display_names.items:
        print(x)
    return render_template('personal/followers.html', display=display_names, 
        user=user)

@personal.route('/-following/<int:id>')
def following_ajax(id):
    page = int(request.args.get('page'))
    user = User.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = db.session.query(User.id, Recommendation, Relationship)\
        .join(Recommendation)\
        .join(Relationship, Relationship.follower == User.id)\
        .filter(User.id.in_([one.following for one in user.following]),
            Recommendation.verification>0)\
        .order_by(desc(Relationship.timestamp))\
        .group_by(User.id)\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/following-macro.html', 'ajax')
    return jsonify({
        'last': display_names.pages in (0, display_names.page),
        'ajax_request': to_return(display_names, _moment, current_user, 
            link=url_for('personal.following', id=id))}) 

@personal.route('/following/<int:id>')
@personal.route('/following')
def following(id=-1):
    if current_user.is_authenticated and id == -1:
        id = current_user.id
    user = User.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = db.session.query(Recommendation)\
        .join(User)\
        .join(Relationship, Relationship.follower == User.id)\
        .filter(User.id.in_([one.following for one in user.following]),
            Recommendation.verification>0)\
        .order_by(desc(Relationship.timestamp))\
        .group_by(User.id)\
        .paginate(1, per_page=current_user.display, error_out=False)
    print(display_names.items[0])
    return render_template('personal/following.html', display=display_names, 
        user = user)

@personal.route('/-inspiration')
@login_required
def inspiration_ajax():
    page = int(request.args.get('page'))
    display_recs = Recommendation.query\
        .filter(Recommendation.user_id.in_([one.following for one in current_user.following]), 
            Recommendation.verification>0)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({
        'last': display_recs.pages in (0, display_recs.page),
        'ajax_request': to_return(display_recs, _moment, current_user, 
            link=url_for('personal.inspiration'))}) 

@personal.route('/inspiration')
@login_required
def inspiration():
    display_recs = Recommendation.query\
        .filter(Recommendation.user_id.in_([one.following for one in current_user.following]), 
            Recommendation.verification>0)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/inspiration.html', display=display_recs)

@personal.route('/-post')
@login_required
def post_ajax():
    page = int(request.args.get('page'))
    display_recs = Recommendation.query\
        .filter(Recommendation.verification>0,
            Recommendation.user_id==current_user.id)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({
        'last': display_recs.pages in (0, display_recs.page),
        'ajax_request': to_return(display_recs, _moment, current_user, 
            link=url_for('personal.post'))})
    
@personal.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm(request.form)
    if request.method == 'POST':
        if form.validate():
            ver = form.public.data
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
    display_recs = Recommendation.query\
        .filter(Recommendation.verification>0,
            Recommendation.user_id==current_user.id)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/post.html', form=form, display=display_recs)

@personal.route('/-profile-com/<int:id>')
def profile_com_ajax(id):
    page = int(request.args.get('page'))
    display_comments = Comment.query\
        .filter(Comment.user_id==id, Comment.verification>0)\
        .order_by(desc(Comment.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/comment-macro.html', 'ajax')
    return jsonify({
        'last': display_comments.pages in (0, display_comments.page),
        'ajax_request': to_return(display_comments, _moment, current_user, 
            link=url_for('personal.profile', id=id))}) 

@personal.route('/-profile-rec/<int:id>')
def profile_ajax(id):
    page = int(request.args.get('page'))
    if(current_user.id == id):
        private = 0
    else:
        private = 1
    display_recs = Recommendation.query\
        .filter(Recommendation.user_id==id, Recommendation.verification>=private)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out = False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({
        'last': display_recs.pages in (0, display_recs.pages),
        'ajax_request': to_return(display_recs, _moment, current_user, 
            link=url_for('personal.profile', id=id))}) 

@personal.route('/profile')
@personal.route('/profile/<int:id>')
def profile(id=-1):
    if id == -1:
        if current_user.is_authenticated:
            id = current_user.id
        else:
            return redirect(url_for('auth.login', next='personal/profile'))
    user = User.query\
        .filter_by(id=id)\
        .first_or_404()
    com_count = 0
    rec_count = 0
    if current_user.is_moderator() and current_user.id == id:
        com_count = Comment.query\
            .filter_by(verification=1)\
            .count()
        rec_count = Recommendation.query\
            .filter_by(verification=1)\
            .count()
    ver_case = case([(db.true() if current_user.id==id else db.false(), 0),], else_=1)
    display_recs = user.recommendation\
        .filter(Recommendation.verification>=ver_case)\
        .order_by(desc(Recommendation.timestamp))
    display_comments = user.comment\
        .filter(Comment.verification>0)\
        .order_by(desc(Comment.timestamp))
    if current_user.id == id:
        for rec in display_recs:
            if rec.made_private:
                title = rec.title
                if len(rec.title) > 10:
                    title = rec.title[:10] + '...'
                flash("Rec '" + title + "' has been made private due to it's content.")
                rec.made_private = False
                db.session.add(rec)
                db.session.commit()
    display_recs = display_recs\
        .paginate(1, per_page=current_user.display, error_out=False)
    display_comments = display_comments\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/profile.html', user=user, display=display_recs, 
        d_c=display_comments, com_count = com_count, rec_count=rec_count)

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