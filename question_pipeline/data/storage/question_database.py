class QuestionDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None