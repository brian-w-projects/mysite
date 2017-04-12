from flask import get_template_attribute, jsonify, render_template, request
from . import mod
from .. import db
from ..decorators import is_moderator
from ..models import Comments, ComModerations, RecModerations, Recommendation
from flask_login import login_required, current_user
from flask_moment import _moment

@mod.route('/-moderate-recs')
@login_required
@is_moderator
def moderate_recs():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    rec = Recommendation.query\
            .filter_by(id=id)\
            .first_or_404()
    if verify == 'true':
        rec.verification = 2
        db.session.add(rec)
        db.session.commit()
        return jsonify({'verify': True})
    else:
        rec.verification = 0
        rec.made_private = True
        db.session.add(rec)
        db.session.commit()
        return jsonify({'verify': False})

@mod.route('/-verify-recs')
@login_required
@is_moderator
def verify_recs_ajax():
    page = int(request.args.get('page'))
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/moderator/mod-rec-macro.html', 'ajax')        
    return jsonify({
        'last': display_recs.page == display_recs.pages or display_recs.pages == 0,
        'ajax_request': to_return(display_recs, _moment, current_user)}) 

@mod.route('/verify-recs')
@login_required
@is_moderator
def verify_recs():
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('mod/verify-recs.html', display=display_recs)

@mod.route('/-moderate-comments')
@login_required
@is_moderator
def moderate_com():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    com = Comments.query\
        .filter_by(id=id)\
        .first_or_404()
    if verify == 'true':
        com.verification = 2
        db.session.add(com)
        db.session.commit()
        return jsonify({'verify': True})
    else:
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
    to_return = get_template_attribute('macros/moderator/mod-comment-macro.html', 'ajax')
    return jsonify({
        'last': display_comments.page == display_comments.pages or display_comments.pages == 0,
        'ajax_request': to_return(display_comments, _moment, current_user)}) 

@mod.route('/verify-comments')
@login_required
@is_moderator
def verify_comments():
    display_comments = Comments.query\
        .filter_by(verification = 1)\
        .order_by(Comments.timestamp.asc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('mod/verify-comments.html', d_c=display_comments)