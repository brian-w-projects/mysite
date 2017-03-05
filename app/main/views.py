from flask import render_template, session, redirect, url_for, request, abort, flash
from . import main
from .forms import SearchForm, CommentForm, DeleteForm, CommentEditForm
from .. import db
from ..models import Users, Recommendation, Permission, Comments
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from ..email import send_email
from random import randint, sample
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import func, select

@main.route('/')
def index():
    display_recs = []
    if current_user.is_authenticated:
        initial_grab = Recommendation.query.filter_by(public=True)\
            .filter(Recommendation.author_id != current_user.id)\
            .order_by(Recommendation.timestamp.desc())\
            .limit(100)
        my_list = current_user.posts.order_by(Recommendation.timestamp.desc()).limit(10)
        for my_rec in my_list:
            for to_add in initial_grab.from_self().filter(Recommendation.title.contains(my_rec.title)):
                display_recs.append(to_add)
            if len(display_recs) >= 50:
                break
        if len(display_recs) >=5:
            display_recs = sample(display_recs, 5)
        elif len(display_recs) == 0:
            temp = Recommendation.query.filter_by(public=True)\
            .filter(Recommendation.author_id != current_user.id)\
            .order_by(Recommendation.timestamp.desc()).limit(50)
            display_recs = [possible for possible in temp if randint(1,3) == 2]
    return render_template('main/index.html', display = display_recs[:5])

@main.route('/about')
def about():
    temp = Recommendation.query.filter_by(public=True).order_by(Recommendation.timestamp.desc()).limit(50)
    display_recs = [possible for possible in temp if randint(1,3) == 2]
    return render_template('main/about.html', display=display_recs[:5])

@main.route('/_highlight')
def highlight_ajax():
    limit = request.args.get('limit', 5, type=int)
    offset = request.args.get('offset', 0, type=int)
    id = request.args.get('id')
    display_comments = Comments.query.filter_by(posted_on=id)\
        .order_by(Comments.timestamp.desc()).offset(offset).limit(limit)
    return render_template('ajax/commentajax.html', d_c = display_comments)

@main.route('/highlight/<int:id>', methods=['GET', 'POST'])
def highlight(id):
    if current_user.is_authenticated:
        limit=current_user.display
    else:
        limit=10
    form = CommentForm(request.form)
    display_recs = [Recommendation.query.filter_by(id=id).first_or_404()]
    display_comments = display_recs[0].comments.order_by(Comments.timestamp.desc()).limit(limit)
    if current_user.is_authenticated and display_recs[0].author_id == current_user.id:
        display_recs[0].new_comment = False
        db.session.add(display_recs[0])
        db.session.commit()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            abort(403)
        if form.validate():
            to_add = Comments(comment_by=current_user.id, comment_by_user=current_user.username, posted_on=id, comment=form.text.data)
            display_recs[0].new_comment = True
            db.session.add(to_add)
            db.session.add(display_recs[0])
            db.session.commit()
            flash(u'\u2713 Your comment has been successfully posted')
        else:
            flash(u'\u2717 Comment cannot be empty')
        return redirect(url_for('main.highlight', id=id, _scheme='https', _external=True))
    return render_template('main/highlight.html', display=display_recs, d_c=display_comments, form=form)

@main.route('/highlight/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_delete(id):
    form = DeleteForm(request.form)
    display_comments = [Comments.query.filter_by(id=id).first_or_404()]
    display_recs = [Recommendation.query.filter_by(id=display_comments[0].posted_on).first_or_404()]
    if display_recs[0].author_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            db.session.delete(display_comments[0])
            db.session.commit()
            flash(u'\u2713 Comment has been deleted')
            return redirect(url_for('main.highlight', id=display_recs[0].id, _scheme='https', _external=True))
        else:
            flash(u'\u2717 You must confirm deletion')
            return redirect(url_for('main.comment_delete', id=id, _scheme='https', _external=True))
        return redirect(url_for('main.comment_delete', id=id, _scheme='https', _external=True))
    return render_template('main/delete.html', form=form, display=display_recs, d_c=display_comments)

@main.route('/highlight/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_edit(id):
    form = CommentEditForm(request.form)
    display_comments = [Comments.query.filter_by(id=id).first_or_404()]
    display_recs = [Recommendation.query.filter_by(id=display_comments[0].posted_on).first_or_404()]
    if display_comments[0].comment_by != current_user.id:
        abort(403)
    if request.method == 'POST':
        if form.validate():
            if form.delete.data:
                db.session.delete(display_comments[0])
                db.session.commit()
                flash(u'\u2713 Comment deleted')
                return redirect(url_for('main.highlight', id=display_recs[0].id, _scheme='https', _external=True))
            else:
                display_comments[0].comment = form.text.data
                db.session.add(display_comments[0])
                db.session.commit()
                flash(u'\u2713 Comment updated')
                return redirect(url_for('main.highlight', id=display_recs[0].id, _scheme='https', _external=True))
        else:
            flash(u'\u2717 Comment must contain text')
            return redirect(url_for('main.comment_edit', id=id, _scheme='https', _external=True))
    form.text.data = display_comments[0].comment
    return render_template('main/commentedit.html', form=form, display=display_recs, d_c=display_comments)

@main.route('/_surprise')
def surprise_ajax():
    limit = request.args.get('limit', 5, type=int)
    temp = Recommendation.query.filter_by(public=True).order_by(Recommendation.timestamp.desc()).limit(5*limit)\
        .from_self().order_by(func.random()).limit(limit)
    return render_template('ajax/postajax.html', display = temp)

@main.route('/surprise')
def surprise(limit=10):
    if current_user.is_authenticated:
        limit = current_user.display
    temp = Recommendation.query.filter_by(public=True).order_by(Recommendation.timestamp.desc()).limit(5*limit)
    display_recs = [possible for possible in temp if randint(1,3) == 2]
    return render_template('main/surprise.html', display=display_recs[:limit], limit=limit)

@main.route('/_search', methods=['POST'])
def search_ajax():
    type = request.form['type']
    search = request.form['search']
    user = request.form['user']
    if request.form['date'] != '':
        date = datetime.strptime(request.form['date'], '%m/%d/%Y')
    else:
        date = ''
    session['search'] = search
    session['user'] = user
    session['date'] = date
    session['type'] = type
    if current_user.is_authenticated:
        limit = current_user.display
    else:
        limit = 10
    
    if type == 'Recs':
        display_recs = Recommendation.query.filter_by(public=True)
        if search != '':
            display_recs = display_recs.filter(Recommendation.title.contains(search))
        if user != '':
            me = Users.query.filter_by(username=user).first()
            display_recs = display_recs.filter_by(author_id=me.id)
        if date != '':
            date = date + timedelta(days=1)
            display_recs = display_recs.filter(Recommendation.timestamp <= date)
        display_recs = display_recs.order_by(Recommendation.timestamp.desc()).limit(limit)
        return render_template('ajax/postajax.html', display = display_recs)
    else:
        display_comments = Comments.query
        if search != '':
            display_comments = display_comments.filter(Comments.comment.contains(search))
        if user != '':
            display_comments = display_comments.filter_by(comment_by_user=user)
        if date != '':
            date = date + timedelta(days=1)
            display_comments = display_comments.filter(Comments.timestamp <= date)
        display_comments = display_comments.order_by(Comments.timestamp.desc()).limit(limit)
        return render_template('ajax/commentajax.html', d_c = display_comments)
    

@main.route('/_additional_results')
def more_ajax():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    type = session['type']
    search = session['search']
    user = session['user']
    date = session['date']
    
    if type == 'Recs':
        display_recs = Recommendation.query.filter_by(public=True)
        if search != '':
            display_recs = display_recs.filter(Recommendation.title.contains(search))
        if user != '':
            me = Users.query.filter_by(username=user).first()
            display_recs = display_recs.filter_by(author_id=me.id)
        if date != '':
            date = date + timedelta(days=1)
            display_recs = display_recs.filter(Recommendation.timestamp <= date)
        display_recs = display_recs.order_by(Recommendation.timestamp.desc()).offset(offset).limit(limit)
        return render_template('ajax/postajax.html', display = display_recs)
    else:
        display_comments = Comments.query
        if search != '':
            display_comments = display_comments.filter(Comments.comment.contains(search))
        if user != '':
            display_comments = display_comments.filter_by(comment_by_user=user)
        if date != '':
            date = date + timedelta(days=1)
            display_comments = display_comments.filter(Comments.timestamp <= date)
        display_comments = display_comments.order_by(Comments.timestamp.desc()).offset(offset).limit(limit)
        return render_template('ajax/commentajax.html', d_c = display_comments)
    

@main.route('/search')
def search():
    display_recs = []
    form = SearchForm(request.form)
    return render_template('main/search.html', form=form, display=display_recs)