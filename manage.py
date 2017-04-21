#!usr/bin/env python
from flask import redirect, request, url_for
from app import create_app, db
from app.models import Comments, ComModerations, Followers, RecModerations, Recommendation, Role, Users
from flask_script import Manager, Server, Shell
from flask_migrate import Migrate, MigrateCommand
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Users=Users, Role=Role, Recommendation=Recommendation,\
        Comments=Comments, Followers=Followers)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0', port='8080'))

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
    # with app.app_context():
        # db.drop_all()
        # db.create_all()
        # Role.generate_roles()
        # user = Users(username='njpsychopath', email='njpsychopath@gmail.com', password='123456789', confirmed=True, role_id = 1)
        # db.session.add(user)
        # user2 = Users(username='njpsy', email='example@example.com', password='123456789', confirmed=True, role_id = 2)
        # db.session.add(user2)
        # Users.generate_users(100, [user, user2])
        # print('Finished users')
        # Recommendation.generate_recs(500)
        # print('Finished recs')
        # Comments.generate_comments(1000)
        # print('Finished comments')
        # Followers.generate_followers(500)
        # print('Finished followers')
        # RecModerations.generate_recmods()
        # print('Finished recmods')
        # ComModerations.generate_commods()
        # print('Finished commods')
        # db.session.commit()
    manager.run()