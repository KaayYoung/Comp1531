from app import db as DB

class Enrolment(DB.Model):
    __tablename__ = 'enrolment'

    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    offering_id = DB.Column('offering_id', DB.Integer, DB.ForeignKey('offering.id'), nullable = False)
    user_id = DB.Column('user_id', DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'), nullable = False)

    def __init__(self, offering_id, user_id):
        self.offering_id = offering_id
        self.user_id = user_id
