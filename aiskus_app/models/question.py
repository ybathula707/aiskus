import time


class Question:
    """ Lightweight class/model to represent a question sent to the /POST frontend API from an asker."""
    
    __slots__ = ('question_body', 'question_asked_time')

    """
        python class objects are by default mutable dictionaries. 
        They can be dynamically modified and extended at runtime.

        __slots__ is a special varible that, once declared, prohibits class objects from being 
        dynamically modified at runitme, the objects are constrained attributes defined within
        this special varible.

        This is a performance optimization; it reduces memory overhead and speeds up lookup access,
        especially important since we'll need to define DB access pattern for quesitons later on.
        
    """

    def __init__(self, question_body: str, question_asked_time: int =None):
        """ 
            Initialize a Question object with a question body and an optional creation time.
            If no creation time is provided, it defaults to the current time in seconds since the epoch.

            :param question_body: The text of the question being asked.
            :param question_asked_time: The time the question was asked, in seconds. 
                If None, defaults to obj creation time (current time).
        """
        self.question_body = question_body
        self.question_asked_time = question_asked_time or int(time.time())

    def to_dict(self):
        """
            Function to convert the current object to a dictionary and return to caller.
            This is best practive when working with APIs.
            Objects, when converted to dictionaries, are easily serializable to JSON making working
            with APIS, Databases and other tranfer protocols way easier. 
        """
        return{
            'question_body': self.question_body,
            'question_asked_time': self.question_asked_time
        }
    
    def __repr__(self):
        """ 
            Return a string representation of the Question object, showing the question body and the time it was asked.
            
            :return: A string representation of the Question object.

            <Debugging Best Practice>
            This method is called when the object is printed or logged, porviding clear representation 
            of the object's state.
        """
        return f"Question(question_body={self.question_body}, question_asked_time={self.question_asked_time})"