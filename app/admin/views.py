from flask import get_template_attribute, jsonify, render_template, request
from . import admin
from .. import db
from ..decorators import is_administrator
from ..email import send_email
from ..models import Comments, ComModerations, RecModerations, Recommendation, Users
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from flask_moment import _moment

@admin.route('/splash')
@login_required
@is_administrator
def admin_splash():
    week_ago = datetime.today() - timedelta(days=7)
    data = {}
    data['count'] = Users.query.count()
    data['recent_account'] = Users.query\
        .filter(Users.member_since > week_ago )\
        .count()
    data['recent_logins'] = Users.query\
        .filter(Users.last_login > week_ago)\
        .count()
    data['total_recs'] = Recommendation.query.count()
    data['recent_recs'] = Recommendation.query\
        .filter(Recommendation.timestamp > week_ago)\
        .count()
    data['total_comments'] = Comments.query.count()
    data['recent_comments'] = Comments.query\
        .filter(Comments.timestamp > week_ago)\
        .count()
    data['recs_to_mod'] = Recommendation.query\
        .filter(Recommendation.verification == 1)\
        .count()
    data['comments_to_mod'] = Comments.query\
        .filter_by(verification=1)\
        .count()
    data['mods'] = Users.query\
        .filter_by(role_id = 2)\
        .order_by(Users.username)
    data['mods_count'] = data['mods'].from_self()\
        .count()
    return render_template('admin/admin-splash.html', data=data, RecModerations=RecModerations,
        ComModerations=ComModerations, week_ago=week_ago)

@admin.route('/-mod-history-com_ajax/<int:id>')
@login_required
@is_administrator
def mod_com_ajax(id):
    page = int(request.args.get('page'))
    mod = Users.query\
        .filter(Users.role_id != 3)\
        .filter_by(id=id)\
        .first_or_404()
    mod_coms = mod.com_mods\
        .order_by(ComModerations.timestamp.desc())\
        .paginate(page=page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/admin/comment-action-macro.html', 'ajax')
    return jsonify({
        'last': mod_coms.page == mod_coms.pages or mod_coms.pages == 0,
        'ajax_request': to_return(mod_coms, _moment, current_user)}) 

@admin.route('/-change-mod-comment-decision')
@login_required
@is_administrator
def change_mod_comment_decision():
    id = int(request.args.get('id'))
    comment = Comments.query\
        .filter_by(id=id)\
        .first_or_404()
    mod = ComModerations.query\
        .filter_by(mod_on=id)\
        .first_or_404()
    db.session.delete(mod)
    if mod.action:
        comment.verification = 0
        new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action= not mod.action)
        db.session.add(new_mod)
        db.session.add(comment)
    else:
        comment.verification = 2
        new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action= not mod.action)
        db.session.add(new_mod)
        db.session.add(comment)
    db.session.commit()
    return jsonify({'verify': not mod.action})

@admin.route('/-change-mod-decision')
@login_required
@is_administrator
def change_mod_decision():
    id = int(request.args.get('id'))
    rec = Recommendation.query\
        .filter_by(id=id)\
        .first_or_404()
    mod = RecModerations.query\
        .filter_by(mod_on=id)\
        .first_or_404()
    db.session.delete(mod)
    if mod.action:
        rec.verification = 0
        rec.made_private = True
        new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=not mod.action)
        db.session.add(new_mod)
        db.session.add(rec)
    else:
        rec.verification = 2
        rec.made_private = False
        new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=not mod.action)
        db.session.add(new_mod)
        db.session.add(rec)
    db.session.commit()
    return jsonify({'verify': not mod.action})

@admin.route('/-mod-history-rec-ajax/<int:id>')
@login_required
@is_administrator
def mod_rec_ajax(id):
    page = int(request.args.get('page'))
    mod = Users.query\
        .filter(Users.role_id != 3)\
        .filter_by(id=id)\
        .first_or_404()
    mod_recs = mod.rec_mods\
        .order_by(RecModerations.timestamp.desc())\
        .paginate(page=page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/admin/rec-action-macro.html', 'ajax')
    return jsonify({
        'last': mod_recs.page == mod_recs.pages or mod_recs.pages == 0,
        'ajax_request': to_return(mod_recs, _moment, current_user)}) 

@admin.route('/mod-history/<int:id>')
@login_required
@is_administrator
def mod_history(id):
    mod = Users.query\
        .filter(Users.role_id != 3)\
        .filter_by(id=id)\
        .first_or_404()
    mod_recs = mod.rec_mods\
        .order_by(RecModerations.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    mod_coms = mod.com_mods\
        .order_by(ComModerations.timestamp.desc())\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('admin/mod-history.html', mod=mod, mod_recs=mod_recs, mod_coms=mod_coms)