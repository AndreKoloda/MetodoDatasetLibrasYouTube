from pymongo import MongoClient

class MongoDB:

    def __init__(self):
        client = MongoClient()
        self.db = client.get_database('LibrasDB')    
    
    def connect_collection(self, collection = 'channels'):
        return self.db.get_collection(collection)
    