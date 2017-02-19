from flask import render_template, session, redirect, url_for, request, abort, flash
from . import main
from .forms import SearchForm
from .. import db
from ..models import Users, Recommendation, Permission
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from ..email import send_email
from random import randint, sample
from datetime import datetime, timedelta

@main.route('/')
def index():
    display_recs = []
    if current_user.is_authenticated:
        initial_grab = Recommendation.query.filter_by(public=True)\
            .order_by(Recommendation.timestamp.desc())
        for my_rec in initial_grab.filter_by(author_id=current_user.id).limit(10):
            for to_add in initial_grab.filter(Recommendation.title.contains(my_rec.title)):
                if to_add.author_id != current_user.id:
                    display_recs.append(to_add)
                if len(display_recs) >= 50:
                    break
        display_recs = sample(display_recs, 5)
    return render_template('index.html', display = display_recs)

@main.route('/highlight/<int:id>')
def highlight(id):
    display_recs = [Recommendation.query.filter_by(id=id).first_or_404()]
    return render_template('highlight.html', display=display_recs)

@main.route('/surprise/')
def surprise(limit=10):
    if current_user.is_authenticated:
        limit = current_user.display
    temp = Recommendation.query.filter_by(public=True).order_by(Recommendation.timestamp.desc()).limit(5*limit)
    display_recs = [possible for possible in temp if randint(1,3) == 2]
    return render_template('surprise.html', display=display_recs[:limit])
    
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm(request.form)
    display_recs = []
    if request.method == 'POST':
        display_recs = Recommendation.query.filter_by(public=True)
        if form.search.data != '':
            display_recs = display_recs.filter(Recommendation.title.contains(form.search.data))
        if form.user.data != '':
            me = Users.query.filter_by(username=form.user.data).first()
            display_recs = display_recs.filter_by(author_id=me.id)
        if form.date.data != None:
            search_date = form.date.data + timedelta(days=1)
            display_recs = display_recs.filter(Recommendation.timestamp.between(search_date, datetime.utcnow()))
        display_recs = display_recs.order_by(Recommendation.timestamp.desc()).limit(current_user.display)
    return render_template('search.html', form=form, display=display_recs)