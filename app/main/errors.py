from flask import render_template, request, jsonify
from . import main

@main.app_errorhandler(403)
def forbidden_error(e):
    return render_template('errors/403.html', error=e), 403

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', error=e), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', error=e), 500
    
@main.app_errorhandler(400)
def bad_request(e):
    return render_template('errors/404.html', error=e), 400
    
@main.app_errorhandler(405)
def method_not_allowed(e):
    # if request.accept_mimetypes.accept_json:
    #     response = jsonify({'Code': 405, 'message': 'This method header is not allowed'})
    #     response.status_code = 405
    #     return response
    return render_template('errors/404.html', error=e), 405