from flask import jsonify, render_template, request
from . import main

@main.app_errorhandler(400)
def bad_request(e):
    if request.is_json:
        response = jsonify({'Code': 400, 'message': 'This request header is malformed.'})
        response.status_code = 400
        return response
    return render_template('errors/404.html', error=e), 400

@main.app_errorhandler(403)
def forbidden_error(e):
    if request.is_json:
        response = jsonify({'Code': 403, 'message': 'You do not have permission to view this'})
        response.status_code = 403
        return response
    return render_template('errors/403.html', error=e), 403

@main.app_errorhandler(404)
def page_not_found(e):
    if request.is_json:
        response = jsonify({'Code': 404, 'message': 'This page cannot be found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html', error=e), 404

@main.app_errorhandler(405)
def method_not_allowed(e):
    if request.is_json:
        response = jsonify({'Code': 405, 'message': 'This method header is not allowed'})
        response.status_code = 405
        return response
    return render_template('errors/404.html', error=e), 405

@main.app_errorhandler(500)
def internal_server_error(e):
    if request.is_json:
        response = jsonify({'Code': 500, 'message': 'This request has caused an internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html', error=e), 500