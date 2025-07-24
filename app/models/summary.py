import time

class Summary:
    __slots__=('first_question_time', 'last_question_time', 'themes', 'summary', 'queried')

    def __init__(self, first_question_time: int=None, last_question_time: int=None, themes: list[str]=[], summary: str='', queried: bool=False):
        self.first_question_time = first_question_time
        self.last_question_time = last_question_time
        self.themes = themes
        self.summary = summary
        self.queried = False

    def to_dict(self):
        return{
            'first_question_time' : self.first_question_time,
            'last_question_time' : self.last_question_time,
            'themes': self.themes,
            'summary': self.summary,
            'queried': self.queried
        }
    
    def to_db_tuple(self):
        return(
            self.first_question_time,
            self.last_question_time,
            self.themes,
            self.summary,
            self.queried
        )
    
    def __repr__(self):
        return f"The summary for this batch is {self.summary}"
