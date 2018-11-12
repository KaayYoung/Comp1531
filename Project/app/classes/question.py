from app import db as DB

#Todo get rid of question class and rename this to question
class Question(DB.Model):
    __tablename__ = 'question'
    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    question = DB.Column('question', DB.String, nullable = False)
    mandatory = DB.Column('mandatory', DB.Boolean, nullable = False)

    def __init__(self, question, mandatory):
        if type(question) != str or type(mandatory) != bool:
            raise TypeError("Field type Error: question=", question, " mandatory=", mandatory)

        if len(question) == 0:
            raise ValueError("Question is not defined")

        if Question.query.filter_by(question = question).first() is not None:
            raise ValueError("Question already exists in DB")

        self.question = question
        self.mandatory = mandatory

    def add_question(self):
        from sqlite3 import IntegrityError
        try:
            if isinstance(self, Question):
                if Question.query.filter_by(question = self.question, mandatory = self.mandatory).first():
                    raise IntegrityError
                elif self.question == "":
                    raise ValueError
                else:
                    DB.session.add(self)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("Question must be of type Question")
        except AttributeError:
            raise AttributeError("Question does not have the right attributes")
        except IntegrityError:
            raise IntegrityError("Question already exists")
        else:
            DB.session.commit()

    def remove_question(self):
        DB.session.delete(Question.query.filter_by(question = self.question, mandatory = self.mandatory).first())
        DB.session.commit()


    #   if pool is None:
    #       self._question_pool = {}
    #   else:
    #       self._question_pool = pool

    # @property
    # def question_pool(self):
    #   return self._question_pool

    # @question_pool.setter
    # def question_pool(self, new_question_pool):
    #   self._question_pool = new_question_pool

    # def delete(self, id):
    #   if id in self.question_pool:
    #       del self.question_pool[id]
        
    # def add(self, question):
    #   self.question_pool[question.id] = question