from flask import render_template, request, redirect, url_for, session, flash, jsonify, get_template_attribute
from flask_moment import _moment
from . import mod
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, RecModerations, ComModerations
from .. import db
from ..email import send_email
from ..decorators import is_moderator
import json

@mod.route('/-moderate')
@login_required
@is_moderator
def moderate_ajax():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    if verify == 'true':
        rec = Recommendation.query.filter_by(id=id).first_or_404()
        rec.verification = 2
        db.session.add(rec)
        db.session.commit()
        return jsonify({'verify': True})
    else:
        rec = Recommendation.query.filter_by(id=id).first_or_404()
        rec.verification = 0
        rec.made_private = True
        db.session.add(rec)
        db.session.commit()
        return jsonify({'verify': False})

@mod.route('/-verify')
@login_required
@is_moderator
def verify_ajax():
    page = int(request.args.get('page'))
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/moderator-rec-macro.html', 'ajax')        
    return jsonify({'last': display_recs.page == display_recs.pages,
        'ajax_request': to_return(display_recs, _moment, current_user)}) 

@mod.route('/verify')
@login_required
@is_moderator
def verify():
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('mod/verify-recs.html', display=display_recs)

@mod.route('/-moderate-com')
@login_required
@is_moderator
def moderate_com_ajax():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    if verify == 'true':
        com = Comments.query.filter_by(id=id).first_or_404()
        com.verification = 2
        db.session.add(com)
        db.session.commit()
        return jsonify({'verify': True})
    else:
        com = Comments.query.filter_by(id=id).first_or_404()
        com.verificition = 0
        db.session.add(com)
        db.session.commit()
        return jsonify({'verify': False})

@mod.route('/-verify-comments')    
@login_required
@is_moderator
def verify_com_ajax():
    page = int(request.args.get('page'))
    display_comments = Comments.query\
        .filter(Comments.verification == 1)\
        .order_by(Comments.timestamp.asc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/moderator-comment-macro.html', 'ajax')
    return jsonify({'last': display_comments.page == display_comments.pages,
        'ajax_request': to_return(display_comments, _moment, current_user)}) 

@mod.route('/verify-comments')
@login_required
@is_moderator
def verify_comments():
    display_comments = Comments.query\
        .filter(Comments.verification == 1)\
        .order_by(Comments.timestamp.asc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('mod/verify-comments.html', d_c=display_comments)