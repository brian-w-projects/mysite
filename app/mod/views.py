from flask import render_template, request, redirect, url_for, session, flash
from . import mod
from .forms import VerifyForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Permission
from .. import db
from ..email import send_email
from ..decorators import permission_required

@mod.route('/verify', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def verify():
    form = VerifyForm(request.form)
    display_recs = Recommendation.query.filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc()).limit(2)
    return render_template('mod/verify.html', form=form, display=display_recs)