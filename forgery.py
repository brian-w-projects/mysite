
@staticmethod
def generate_users(count=100):
    from sqlalchemy.exc import IntegrityError
    from random import seed, randint
    import forgery_py
    
    seed()
    for i in range(count):
        u = Users(username=forgery_py.internet.user_name(True),
            email=forgery_py.internet.email_address(),
            password=forgery_py.lorem_ipsum.word(),
            confirmed=True,
            about_me=forgery_py.lorem_ipsum.sentences(randint(3,5)),
            member_since=forgery_py.date.date(True))
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    
@staticmethod
def generate_recs(count=1000):
    from random import seed, randint
    import forgery_py
    
    seed()
    user_count=Users.query.count()
    for i in range(count):
        u = Users.query.offset(randint(0, user_count - 1)).first()
        
        r = Recommendation(title=forgery_py.lorem_ipsum.sentence(),
            public=randint(0,10)>8,
            timestamp=forgery_py.date.date(True),
            author=u,
            text=forgery_py.lorem_ipsum.sentences(randint(2,8)))
        
        db.session.add(r)
        db.session.commit()
        
    
    