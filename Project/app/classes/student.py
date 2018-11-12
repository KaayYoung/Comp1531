from app import db as DB
from app.classes.user import User

class Student(User):

    __tablename__ = 'student'
    _id = DB.Column('id', DB.Integer, DB.ForeignKey('user.id'), primary_key = True, nullable = False)

    __mapper_args__ = {
        'polymorphic_identity':'student',
    }

    def __init__(self, id, name, password):
        super().__init__(password=password, id=id, name=name)

    def __repr__(self):
        return '<Student {0} | {1}>'.format(self.id, self.password)
