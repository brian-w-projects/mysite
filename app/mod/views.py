from flask import render_template, request, redirect, url_for, session, flash
from . import mod
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Permission
from .. import db
from ..email import send_email
from ..decorators import permission_required
import json

@mod.route('/_moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_ajax():
    id = request.args.get('id')
    verify = request.args.get('verify')
    if verify is True:
        rec = Recommendation.query.filter_by(id=id).first_or_404()
        rec.verification = 2
        db.session.add(rec)
        db.session.commit()
        return json.dumps({'verified':True}), 200, {'ContentType':'application/json'} 
    else:
        rec = Recommendation.query.filter_by(id=id).first_or_404()
        rec.verification = 0
        rec.public = False
        rec.made_private = True
        db.session.add(rec)
        db.session.commit()
        return json.dumps({'verified':False}), 200, {'ContentType':'application/json'} 

@mod.route('/_verify')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def verify_ajax():
    session['offset'] += 0
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .offset(session['offset'])\
        .limit(current_user.display)
    return render_template('ajax/postajax.html', display = display_recs)

@mod.route('/verify')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def verify():
    session['offset'] = 0
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .limit(current_user.display)
    return render_template('mod/verify.html', display=display_recs)