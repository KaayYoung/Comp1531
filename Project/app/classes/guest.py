from app import db as DB
from app.classes.user import User

class Guest(User):

    __tablename__ = 'guest'
    _id = DB.Column('id', DB.Integer, DB.ForeignKey('user.id'), primary_key = True, nullable = False)
    _active = DB.Column('active', DB.Boolean, nullable = False)
    _offering_request = DB.Column('offering_request', DB.String, DB.ForeignKey('offering.id'), nullable = False)

    offering = DB.relationship('Offering', lazy='joined')

    __mapper_args__ = {
        'polymorphic_identity':'guest',
    }

    def __init__(self, password, offering_request , active=False, id=None, name=None):
        super().__init__(password=password, id=id, name=name)
        self._active = active
        self._offering_request = offering_request

    def __repr__(self):
        return '<Guest {0} | {1}>'.format(self.id, self.password)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active
        
    @property
    def offering_request(self):
        return self._offering_request

    @offering_request.setter
    def offering_request(self, offering_request):
        self._offering_request = offering_request

    @property
    def is_active(self):
        return self.active

    def check_login(self, password):
        if password == self.password and self.active:
            return True
        else:
            return False
