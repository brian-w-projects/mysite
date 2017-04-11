from flask import render_template, request, redirect, url_for, session, abort, flash, get_template_attribute, jsonify
from . import personal
from .forms import ChangeForm, PostForm, EditForm, CommentEditForm, DeleteForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, Followers
from .. import db
from ..email import send_email
from datetime import datetime
import json
from flask_moment import _moment

@personal.route('/comment-delete/<int:id>', methods=['GET', 'POST'])
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
            redirect_to = request.args.get('after', default='personal.profile').split('_')[0]
            if 'highlight' in redirect_to:
                return redirect(url_for(redirect_to, id=display_comments.posted_on))
            return redirect(url_for(redirect_to))
        else:
            flash(u'\u2717 You must confirm deletion')
            return redirect(url_for('personal.comment_delete', id=id, after=request.args.get('after', default=None)))
    return render_template('personal/comment-delete.html', form=form, rec=display_recs, com=display_comments,
        after=request.args.get('after', default=None))

@personal.route('/comment-edit/<int:id>', methods=['GET', 'POST'])
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
            else:
                display_comments.comment = form.text.data
                db.session.add(display_comments)
                db.session.commit()
                flash(u'\u2713 Comment updated')
            if 'highlight' in request.args.get('after', default='personal.profile'):
                return redirect(url_for(request.args.get('after', default='personal.profile'), id=display_comments.posted_on))
            redirect_to = request.args.get('after', default='personal.profile').split('_')[0]
            return redirect(url_for(redirect_to))
        else:
            flash(u'\u2717 Comment must contain text')
            return redirect(url_for('personal.comment_edit', id=id, after=request.args.get('after', default=None)))
    form.text.data = display_comments.comment
    return render_template('personal/comment-edit.html', form=form, rec=display_recs, com=display_comments,
        after=request.args.get('after', default=None))

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
                display_recs.verification = -1
                db.session.add(display_recs)
                for com in display_recs.comments:
                    com.verification = 0
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
                db.session.commit()
                flash(u'\u2713 Your rec has been edited')
            if 'highlight' in request.args.get('after', default='personal.profile'):
                return redirect(url_for(request.args.get('after', default='personal.profile'), id=post_id))
            redirect_to = request.args.get('after', default='personal.profile').split('_')[0]
            return redirect(url_for(redirect_to))
        else:
            if 'title' in form.errors:
                flash(u'\u2717 Recs must contain a title')
            if 'text' in form.errors:
                flash(u'\u2717 Recs must contain text')
            if 'delete' in form.errors:
                flash(u'\u2717 Check both boxes to delete this rec')
            return redirect(url_for('personal.edit', post_id=post_id, after=request.args.get('after', default=None)))
    form.title.data = display_recs.title
    form.public.data = display_recs.verification > 0
    form.text.data = display_recs.text
    return render_template('personal/edit.html', form=form, after=request.args.get('after', default='personal.profile').split('_')[0])

@personal.route('/-followers/<int:id>')
def followers_ajax(id):
    page = int(request.args.get('page'))
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = user\
        .followed_by\
        .order_by(Followers.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/followed-macro.html', 'ajax')
    return jsonify({'last': display_names.page == display_names.pages,
        'ajax_request': to_return(display_names, _moment, current_user, Recommendation)}) 

@personal.route('/followers/<int:id>')
@personal.route('/followers')
def followers(id=-1):
    if current_user.is_authenticated and id == -1:
        id = current_user.id
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = user\
        .followed_by\
        .order_by(Followers.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/followers.html', display=display_names, 
        user=user, Recommendation=Recommendation)

@personal.route('/-follow')
@login_required
def follow_ajax():
    id = int(request.args.get('id'))
    if current_user.id == id:
        return jsonify({'added':False}) 
    user = current_user.following.filter_by(following=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'added':False}) 
    else:
        addition = Followers(follower=current_user.id, following=id)
        db.session.add(addition)
        db.session.commit()
        return jsonify({'added':True})

@personal.route('/-following/<int:id>')
def following_ajax(id):
    page = int(request.args.get('page'))
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = user.following\
        .order_by(Followers.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/following-macro.html', 'ajax')
    return jsonify({'last': display_names.page == display_names.pages,
        'ajax_request': to_return(display_names, _moment, current_user, Recommendation)}) 


@personal.route('/following/<int:id>')
@personal.route('/following')
def following(id=-1):
    if current_user.is_authenticated and id == -1:
        id = current_user.id
    user = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    display_names = user\
        .following\
        .order_by(Followers.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/following.html', display=display_names, 
        user = user, Recommendation=Recommendation)

@personal.route('/-inspiration')
@login_required
def inspiration_ajax():
    page = int(request.args.get('page'))
    following = [x.who.id for x in current_user.following]
    display_recs = Recommendation.query\
        .filter(Recommendation.author_id.in_(following))\
        .filter(Recommendation.verification > 0)\
        .order_by(Recommendation.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({'last': display_recs.page == display_recs.pages,
        'ajax_request': to_return(display_recs, _moment, current_user)}) 

@personal.route('/inspiration')
@login_required
def inspiration():
    following = [x.who.id for x in current_user.following]
    display_recs = Recommendation.query\
        .filter(Recommendation.author_id.in_(following))\
        .filter(Recommendation.verification > 0)\
        .order_by(Recommendation.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/inspiration.html', display=display_recs)

@personal.route('/-post')
@login_required
def post_ajax():
    page = int(request.args.get('page'))
    display_recs = Recommendation.query\
        .filter_by(author_id=current_user.id)\
        .order_by(Recommendation.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({'last': display_recs.page == display_recs.pages,
        'ajax_request': to_return(display_recs, _moment, current_user)})
    

@personal.route('/post', methods=['GET', 'POST'])
@login_required
def post():
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
        return redirect(url_for('personal.post'))
    display_recs = Recommendation.query\
        .filter_by(author_id=current_user.id)\
        .order_by(Recommendation.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/post.html', form=form, display=display_recs)

@personal.route('/-profile-com/<int:id>')
def profile_com_ajax(id):
    page = int(request.args.get('page'))
    display_comments = Comments.query\
        .filter_by(comment_by=id)\
        .filter(Comments.verification > 0)\
        .order_by(Comments.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/comment-macro.html', 'ajax')
    return jsonify({'last': display_comments.page == display_comments.pages,
        'ajax_request': to_return(display_comments, _moment, current_user)}) 

@personal.route('/-profile/<int:id>')
def profile_ajax(id):
    page = int(request.args.get('page'))
    if(current_user.id == id):
        private = 0
    else:
        private = 1
    display_recs = Recommendation.query\
        .filter_by(author_id=id)\
        .filter(Recommendation.verification >= private)\
        .order_by(Recommendation.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out = False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({'last': display_recs.page == display_recs.pages,
        'ajax_request': to_return(display_recs, _moment, current_user)}) 

@personal.route('/profile')
@personal.route('/profile/<int:id>')
def profile(id=-1):
    com_count = 0
    rec_count = 0
    if id == -1 and current_user.is_authenticated:
        id = current_user.id
    elif id == -1 and not current_user.is_authenticated:
        return redirect(url_for('auth.login', next='personal/profile'))
    if current_user.is_authenticated:
        if current_user.is_moderator() and current_user.id == id:
            com_count = Comments.query\
                .filter_by(verification=1)\
                .count()
            rec_count = Recommendation.query\
                .filter_by(verification=1)\
                .count()
    user = Users.query.\
        filter_by(id=id)\
        .first_or_404()
    if current_user.is_authenticated and current_user.id == id:
        private = 0
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
    else: 
        private = 1
    display_recs = user.posts\
        .filter(Recommendation.verification >= private)\
        .order_by(Recommendation.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    display_comments = user.commented_on\
        .filter(Comments.verification > 0)\
        .order_by(Comments.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('personal/profile.html', user=user, display=display_recs, 
        d_c=display_comments, id=id, com_count = com_count, rec_count=rec_count)

@personal.route('/-token')
@login_required
def token_ajax():
    current_user.generate_auth_token()
    return current_user.api

@personal.route('/token')
@login_required
def token():
    if not current_user.api:
        current_user.generate_auth_token()
    return render_template('personal/token.html')

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
        return redirect(url_for('personal.update'))
    form.about_me.data = current_user.about_me
    form.limit.data= str(current_user.display)
    return render_template('personal/update.html', form=form)