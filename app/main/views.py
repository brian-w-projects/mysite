from flask import render_template, session, redirect, url_for, request, abort, flash
from . import main
from .forms import SearchForm, CommentForm
from .. import db
from ..models import Users, Recommendation, Comments
from flask_login import login_required, current_user
from ..decorators import is_administrator
from ..email import send_email
from random import randint, sample
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import func, select

@main.route('/about')
def about():
    temp = Recommendation.query\
        .filter(Recommendation.verification > 0)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(50)
    display_recs = [possible for possible in temp if randint(1,3) == 2]
    return render_template('main/about.html', display=display_recs[:5])

@main.route('/_highlight')
def highlight_ajax():
    session['offset'] += session['limit']
    display_comments = Comments.query\
        .filter(Comments.verification != 0)\
        .filter_by(posted_on=session['id'])\
        .order_by(Comments.timestamp.desc())\
        .offset(session['offset'])\
        .limit(session['limit'])
    return render_template('ajax/commentajax.html', d_c = display_comments)

@main.route('/highlight/<int:id>', methods=['GET', 'POST'])
def highlight(id):
    if current_user.is_authenticated:
        session['limit']=current_user.display
    else:
        session['limit']=10
    session['offset']=0
    session['id']=id
    form = CommentForm(request.form)
    display_recs = Recommendation.query.filter_by(id=id).first_or_404()
    if display_recs.verification <= 0 and display_recs.author_id != current_user.id:
            abort(403)
    display_comments = display_recs.comments\
        .filter(Comments.verification != 0)\
        .order_by(Comments.timestamp.desc())\
        .limit(session['limit'])
    if current_user.is_authenticated and display_recs.author_id == current_user.id:
        display_recs.new_comment = False
        db.session.add(display_recs)
        db.session.commit()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            abort(403)
        if form.validate():
            to_add = Comments(comment_by=current_user.id, 
                posted_on=id, 
                comment=form.text.data)
            display_recs.new_comment = True
            db.session.add(to_add)
            db.session.add(display_recs)
            db.session.commit()
            flash(u'\u2713 Your comment has been successfully posted')
        else:
            flash(u'\u2717 Comment cannot be empty')
        return redirect(url_for('main.highlight', id=id, _scheme='https', _external=True))
    return render_template('main/highlight.html', rec=display_recs, d_c=display_comments, form=form)

@main.route('/')
def index():
    display_recs = []
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for('admin.admin_splash', _scheme='https', _external=True))
        initial_grab = Recommendation.query\
            .filter(Recommendation.verification > 0)\
            .filter(Recommendation.author_id != current_user.id)\
            .order_by(Recommendation.timestamp.desc())\
            .limit(100)
        my_list = current_user.posts\
            .order_by(Recommendation.timestamp.desc())\
            .limit(10)
        for my_rec in my_list:
            for to_add in initial_grab.from_self().filter(Recommendation.title.contains(my_rec.title)):
                display_recs.append(to_add)
            if len(display_recs) >= 50:
                break
        if len(display_recs) >=5:
            display_recs = sample(display_recs, 5)
        elif len(display_recs) == 0:
            temp = Recommendation.query\
                .filter(Recommendation.verification > 0)\
                .filter(Recommendation.author_id != current_user.id)\
                .order_by(Recommendation.timestamp.desc())\
                .limit(50)
            display_recs = [possible for possible in temp if randint(1,3) == 2]
    return render_template('main/index.html', display = display_recs[:5])

@main.route('/_search', methods=['POST'])
def search_ajax():
    session['type'] = request.form['type']
    session['search'] = request.form['search']
    session['user'] = request.form['user']
    if request.form['date'] != '':
        session['date'] = datetime.strptime(request.form['date'], '%m/%d/%Y') + timedelta(days=1)
    else:
        session['date'] = ''
    if current_user.is_authenticated:
        session['limit'] = current_user.display
    else:
        session['limit'] = 10
    session['offset'] = 0
    return search_query()
    
@main.route('/_additional_results')
def more_ajax():
    session['offset'] += session['limit']
    return search_query()

def search_query():
    if session['type'] == 'Recs':
        display_recs = Recommendation.query\
            .filter(Recommendation.verification > 0)
        if session['search'] != '':
            display_recs = display_recs.filter(Recommendation.title.contains(session['search']))
        if session['user'] != '':
            me = Users.query\
                .filter_by(username=session['user'])\
                .first()
            display_recs = display_recs.filter_by(author_id=me.id)
        if session['date'] != '':
            display_recs = display_recs.filter(Recommendation.timestamp <= session['date'])
        display_recs = display_recs\
            .order_by(Recommendation.timestamp.desc())\
            .offset(session['offset'])\
            .limit(session['limit'])
        return render_template('ajax/postajax.html', display = display_recs)
    else:
        display_comments = Comments.query.filter_by(verification=1)
        if session['search'] != '':
            display_comments = display_comments\
                .filter(Comments.comment.contains(session['search']))
        if session['user'] != '':
            display_comments = display_comments\
                .filter_by(comment_by_user=session['user'])
        if session['date'] != '':
            display_comments = display_comments\
                .filter(Comments.timestamp <= session['date'])
        display_comments = display_comments\
            .order_by(Comments.timestamp.desc())\
            .offset(session['offset'])\
            .limit(session['limit'])
        return render_template('ajax/commentajax.html', d_c = display_comments)
    
@main.route('/search')
def search():
    form = SearchForm(request.form)
    return render_template('main/search.html', form=form)
    
@main.route('/_surprise')
def surprise_ajax():
    temp = Recommendation.query\
        .filter(Recommendation.verification > 0)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(5*session['limit'])\
        .from_self().order_by(func.random())\
        .limit(session['limit'])
    return render_template('ajax/postajax.html', display = temp)

@main.route('/surprise')
def surprise():
    if current_user.is_authenticated:
        session['limit'] = current_user.display
    else:
        session['limit']=10
    display_recs = Recommendation.query\
        .filter(Recommendation.verification > 0)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(5*session['limit'])\
        .from_self()\
        .order_by(func.random())\
        .limit(session['limit'])
    return render_template('main/surprise.html', display=display_recs)