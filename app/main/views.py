from flask import render_template, session, redirect, url_for, request, abort, flash, jsonify, get_template_attribute
from . import main
from .forms import SearchForm, CommentForm
from .. import db
from ..models import Users, Recommendation, Comments
from flask_login import login_required, current_user
from ..decorators import is_administrator
from ..email import send_email
from random import randint, sample
from datetime import datetime, timedelta
from flask_moment import _moment
from sqlalchemy.sql.expression import func, select, or_

@main.route('/rec_inline_comment_ajax')
def rec_inline_comment_ajax():
    id = int(request.args.get('id'))
    display_comments = Comments.query\
        .filter_by(posted_on = id)\
        .filter(Comments.verification != 0)\
        .order_by(Comments.timestamp.desc())\
        .paginate(1, per_page=5, error_out=False)
    if len(display_comments.items) == 0:
        return jsonify({'ajax_request': ''}) 
    to_return = get_template_attribute('macros/comment_macro.html', 'ajax_div_wrapper')
    return jsonify({'ajax_request': to_return(display_comments, _moment, current_user)}) 

@main.route('/about')
def about():
    display_recs = Recommendation.query\
        .filter(Recommendation.verification > 0)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(50)\
        .from_self()\
        .order_by(func.random())\
        .limit(5)\
        .from_self()\
        .paginate(1, per_page=5, error_out=False)
    return render_template('main/about.html', display=display_recs)

@main.route('/highlight_ajax/<int:id>')
def load_comments(id):
    page = int(request.args.get('page'))
    display_comments = Comments.query\
        .filter_by(posted_on = id)\
        .filter(Comments.verification != 0)\
        .order_by(Comments.timestamp.desc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/comment_macro.html', 'ajax')
    return jsonify({'last': display_comments.page == display_comments.pages,
        'ajax_request': to_return(display_comments, _moment, current_user)}) 


@main.route('/highlight/<int:id>', methods=['GET', 'POST'])
def highlight(id):
    form = CommentForm(request.form)
    display_recs = Recommendation.query\
        .filter(Recommendation.verification != -1)\
        .filter_by(id=id)\
        .first_or_404()
    if display_recs.verification == 0 and (not current_user.is_authenticated or display_recs.author_id != current_user.id):
        abort(403)
    display_comments = display_recs.comments\
        .filter(Comments.verification > 0)\
        .order_by(Comments.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
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
        return redirect(url_for('main.highlight', id=id))
    return render_template('main/highlight.html', rec=display_recs, d_c=display_comments, 
        form=form)

@main.route('/')
def index():
    display_recs = []
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for('admin.admin_splash'))
        my_list = [max(x.title.split(), key=len) for x in current_user.posts\
            .order_by(Recommendation.timestamp.desc())\
            .limit(10)]
        display_recs = Recommendation.query\
            .filter(Recommendation.verification > 0)\
            .filter(Recommendation.author_id != current_user.id)\
            .filter(or_(*[Recommendation.title.contains(list_ele) for list_ele in my_list]))\
            .order_by(Recommendation.timestamp.desc())\
            .limit(100)\
            .from_self()\
            .order_by(func.random())\
            .limit(5)\
            .from_self()\
            .paginate(1, per_page=5, error_out=False)
    return render_template('main/index.html', display = display_recs)

@main.route('/_search', methods=['POST'])
def search_ajax():
    session['type'] = request.form['type']
    session['search'] = request.form['search']
    session['user'] = request.form['user']
    if request.form['date'] != '':
        session['date'] = datetime.strptime(request.form['date'], '%m/%d/%Y') + timedelta(days=1)
    else:
        session['date'] = ''
    return search_query()
    
@main.route('/_additional_results')
def more_ajax():
    return search_query(page = int(request.args.get('page')))

def search_query(page = 1):
    if session['type'] == 'Recs':
        display_recs = Recommendation.query\
            .filter(Recommendation.verification > 0)
        if session['search'] != '':
            display_recs = display_recs\
                .filter(Recommendation.title.contains(session['search']))
        if session['user'] != '':
            me = Users.query\
                .filter_by(username=session['user'])\
                .first()
            display_recs = display_recs\
                .filter_by(author_id = me.id)
        if session['date'] != '':
            display_recs = display_recs.filter(Recommendation.timestamp <= session['date'])
        display_recs = display_recs\
            .order_by(Recommendation.timestamp.desc())\
            .paginate(page, per_page=current_user.display, error_out=False)
        to_return = get_template_attribute('macros/rec_macro.html', 'ajax')
        return jsonify({'last': display_recs.page == display_recs.pages,
            'ajax_request': to_return(display_recs, _moment, current_user)}) 
    else:
        display_comments = Comments.query\
            .filter(Comments.verification > 0)
        if session['search'] != '':
            display_comments = display_comments\
                .filter(Comments.comment.contains(session['search']))
        if session['user'] != '':
            me = Users.query\
                .filter_by(username=session['user'])\
                .first()
            display_comments = display_comments\
                .filter_by(comment_by=me.id)
        if session['date'] != '':
            display_comments = display_comments\
                .filter(Comments.timestamp <= session['date'])
        display_comments = display_comments\
            .order_by(Comments.timestamp.desc())\
            .paginate(page, per_page=current_user.display, error_out=False)
        to_return = get_template_attribute('macros/comment_macro.html', 'ajax')
        return jsonify({'last': display_comments.page == display_comments.pages,
            'ajax_request': to_return(display_comments, _moment, current_user)}) 
    
@main.route('/search')
def search():
    form = SearchForm(request.form)
    return render_template('main/search.html', form=form)
    
@main.route('/_surprise')
def surprise_ajax():
    display_recs = Recommendation.query\
        .filter(Recommendation.verification > 0)\
        .filter(Recommendation.author_id != current_user.id)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(5*current_user.display)\
        .from_self()\
        .order_by(func.random())\
        .paginate(1, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/rec_macro.html', 'ajax')
    return jsonify({'last': display_recs.page == display_recs.pages,
        'ajax_request': to_return(display_recs, _moment, current_user)}) 

@main.route('/surprise')
def surprise():
    display_recs = Recommendation.query\
        .filter(Recommendation.verification > 0)\
        .filter(Recommendation.author_id != current_user.id)\
        .order_by(Recommendation.timestamp.desc())\
        .limit(5*current_user.display)\
        .from_self()\
        .order_by(func.random())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('main/surprise.html', display=display_recs)