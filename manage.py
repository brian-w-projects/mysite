#!usr/bin/env python
from flask import redirect, request, url_for
from app import create_app, db
from app.models import Comment, Com_Moderation, Relationship, Rec_Moderation, Recommendation, Role, User
from flask_script import Manager, Server, Shell
from flask_migrate import Migrate, MigrateCommand
import os

app = create_app('default')
# app = create_app('deployment')
# app = create_app('production')
migrate = Migrate(app, db)

@app.url_defaults
def hashed_static_file(endpoint, values):
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            blueprint = request.blueprint
            if '.' in endpoint:  # blueprint
                blueprint = endpoint.rsplit('.', 1)[0]

            static_folder = app.static_folder
           # use blueprint, but dont set `static_folder` option
            if blueprint and app.blueprints[blueprint].static_folder:
                static_folder = app.blueprints[blueprint].static_folder

            fp = os.path.join(static_folder, filename)
            if os.path.exists(fp):
                values['_'] = int(os.stat(fp).st_mtime)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)