from flask import get_template_attribute, jsonify, render_template, request
from . import admin
from .. import db
from ..decorators import is_administrator
from ..email import send_email
from ..models import Comments, ComModerations, RecModerations, Recommendation, Users
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from flask_moment import _moment
from sqlalchemy import case
from sqlalchemy.sql.expression import asc, desc, func, distinct

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
    new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action=not mod.action)
    if mod.action:
        comment.verification = 0
    else:
        comment.verification = 2
    db.session.add(new_mod)
    db.session.delete(mod)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'verify': not mod.action})

@admin.route('/-change-mod-rec-decision')
@login_required
@is_administrator
def change_mod_decision():
    id = int(request.args.get('id'))
    rec = Recommendation.query\
        .filter_by(id=id)\
        .first_or_404()
    mod = rec.moderation\
        .first_or_404()
    new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=not mod.action)
    if mod.action:
        rec.verification = 0
        rec.made_private = True
    else:
        rec.verification = 2
        rec.made_private = False
    db.session.add(new_mod)
    db.session.delete(mod)
    db.session.add(rec)
    db.session.commit()
    return jsonify({'verify': not mod.action})

@admin.route('/-mod-history-com-ajax/<int:id>')
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
        'last': mod_coms.pages in (0, mod_coms.page),
        'ajax_request': to_return(mod_coms, _moment, current_user)}) 

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
        'last': mod_recs.pages in (0, mod_recs.page),
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
        .order_by(desc(RecModerations.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    mod_coms = mod.com_mods\
        .order_by(desc(ComModerations.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('admin/mod-history.html', mod=mod,
        mod_recs=mod_recs, mod_coms=mod_coms)
    
@admin.route('/splash')
@login_required
@is_administrator
def admin_splash():
    week_ago = datetime.today() - timedelta(days=7)
    data = {}
    
    users = Users.query
    recommendation = Recommendation.query
    comments = Comments.query
    
    data['count'] = users.count()
    data['recent_account'] = users\
        .filter(Users.member_since>week_ago)\
        .count()
    data['recent_logins'] = users\
        .filter(Users.last_login>week_ago)\
        .count()
    data['total_recs'] = recommendation.count()
    data['recent_recs'] = recommendation\
        .filter(Recommendation.timestamp>week_ago)\
        .count()
    data['recs_to_mod'] = recommendation\
        .filter_by(verification = 1)\
        .count()
    data['total_comments'] = comments.count()
    data['recent_comments'] = comments\
        .filter(Comments.timestamp>week_ago)\
        .count()
    data['comments_to_mod'] = comments\
        .filter_by(verification=1)\
        .count()
    data['mods'] = users\
        .filter_by(role_id=2)\
        .order_by(Users.username)
    data['mods_count'] = data['mods']\
        .count()
    
    
    xpr = case([(RecModerations.timestamp>week_ago, RecModerations.id),])
    xpr_com = case([(ComModerations.timestamp>week_ago, ComModerations.id),])
    
    moderator_info = db.session.query(Users, func.count(distinct(RecModerations.id)), func.count(distinct(xpr)), func.count(distinct(ComModerations.id)), func.count(distinct(xpr_com)))\
        .join(RecModerations)\
        .join(ComModerations)\
        .filter(Users.role_id==2)\
        .group_by(Users.username)\
        .all()
    
    
    
    
    print(moderator_info)

    
    return render_template('admin/splash.html', data=data, 
        RecModerations=RecModerations, ComModerations=ComModerations, 
        week_ago=week_ago)
        
        # moderator_info = db.session.query(Users, func.count(distinct(RecModerations.id)), func.count(distinct(ComModerations.id)))\
        # .join(RecModerations)\
        # .join(ComModerations)\
        # .filter(Users.role_id==2)\
        # .group_by(Users.username)\
        # .all()