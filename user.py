class User(object):
    """
        Represents an Uber user
    """
    def __init__(self, first_name=None, last_name=None, picture=None):
        self.first_name = first_name
        self.last_name = last_name
        self.picture = picture
