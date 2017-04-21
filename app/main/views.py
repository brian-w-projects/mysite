from flask import abort, flash, get_template_attribute, jsonify, redirect, render_template, request, session, url_for
from . import main
from .forms import CommentForm, SearchForm
from .. import db
from ..models import Comments, Recommendation, Users
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from flask_moment import _moment
from sqlalchemy.sql.expression import func, or_, desc

@main.route('/about')
def about():
    display_recs = Recommendation.query\
        .filter_by(verification = 2)\
        .order_by(desc(Recommendation.timestamp))\
        .limit(50)\
        .from_self()\
        .order_by(func.random())\
        .limit(5)\
        .from_self()\
        .paginate(1, per_page=5, error_out=False)
    return render_template('main/about.html', display=display_recs)

@main.route('/highlight-ajax/<int:id>')
def load_comments(id):
    page = int(request.args.get('page'))
    display_comments = Comments.query\
        .filter_by(posted_on = id)\
        .filter(Comments.verification != 0)\
        .order_by(desc(Comments.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/comment-macro.html', 'ajax')
    return jsonify({
        'last': display_comments.pages in (0, display_comments.page),
        'ajax_request': to_return(display_comments, _moment, current_user, link=url_for('main.highlight', id=id))}) 


@main.route('/highlight/<int:id>', methods=['GET', 'POST'])
def highlight(id):
    form = CommentForm(request.form)
    display_recs = Recommendation.query\
        .filter(Recommendation.verification != -1, Recommendation.id == id)\
        .first_or_404()
    if display_recs.verification == 0 and display_recs.author_id != current_user.id:
        abort(403)
    display_comments = display_recs.comments\
        .filter(Comments.verification > 0)\
        .order_by(desc(Comments.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    if display_recs.author_id == current_user.id:
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
    if current_user.is_administrator():
        return redirect(url_for('admin.admin_splash'))
    if current_user.is_authenticated:
        my_list = [max(x.title.split(), key=len) for x in current_user.posts\
            .order_by(Recommendation.timestamp.desc())\
            .limit(10)]
        display_recs = Recommendation.query\
            .filter(Recommendation.verification > 0, Recommendation.author_id != current_user.id)\
            .filter(or_(*[Recommendation.title.contains(list_ele) for list_ele in my_list]))\
            .order_by(desc(Recommendation.timestamp))\
            .limit(100)\
            .from_self()\
            .order_by(func.random())\
            .limit(5)\
            .from_self()\
            .paginate(1, per_page=5, error_out=False)
    else:
        display_recs = None
    return render_template('main/index.html', display = display_recs)

@main.route('/-search', methods=['POST'])
def search_ajax():
    session['type'] = request.form['type']
    session['search'] = request.form['search']
    session['user'] = request.form['user']
    if request.form['date'] != '':
        session['date'] = datetime.strptime(request.form['date'], '%m/%d/%Y') + timedelta(days=1)
    else:
        session['date'] = ''
    return search_query()
    
@main.route('/-additional-results')
def search_more_ajax():
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
            .order_by(desc(Recommendation.timestamp))\
            .paginate(page, per_page=current_user.display, error_out=False)
        to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
        return jsonify({
            'last': display_recs.pages in (0, display_recs.page),
            'ajax_request': to_return(display_recs, _moment, current_user, link=url_for('main.search'))}) 
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
            .order_by(desc(Comments.timestamp))\
            .paginate(page, per_page=current_user.display, error_out=False)
        to_return = get_template_attribute('macros/comment-macro.html', 'ajax')
        return jsonify({
            'last': display_comments.page == display_comments.pages or display_comments.pages == 0,
            'ajax_request': to_return(display_comments, _moment, current_user, link=url_for('main.search'))}) 
    
@main.route('/search')
def search():
    form = SearchForm(request.form)
    return render_template('main/search.html', form=form)
    
@main.route('/-surprise')
def surprise_ajax():
    display_recs = Recommendation.query\
        .filter(Recommendation.verification>0,
            Recommendation.author_id != current_user.id)\
        .order_by(desc(Recommendation.timestamp))\
        .limit(5*current_user.display)\
        .from_self()\
        .order_by(func.random())\
        .paginate(1, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({
        'last': display_recs.pages in (0, display_recs.page),
        'ajax_request': to_return(display_recs, _moment, current_user, link=url_for('main.surprise'))}) 

@main.route('/surprise')
def surprise():
    display_recs = Recommendation.query\
        .filter(Recommendation.verification > 0,
            Recommendation.author_id != current_user.id)\
        .order_by(desc(Recommendation))\
        .limit(5*current_user.display)\
        .from_self()\
        .order_by(func.random())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('main/surprise.html', display=display_recs)

# Alternate Profile URL
@main.route('/u/<string:username>')
def find_user(username):
    user = Users.query\
        .filter_by(username=username)\
        .first_or_404()
    return redirect(url_for('personal.profile', id=user.id))