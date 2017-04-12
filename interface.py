import pyrebase
import os
from datetime import datetime
import time
import json


class FirebaseInterface:

    def __init__(self, fconfig='firebase.config.json'):
        with open(fconfig, 'rt') as f:
            config = json.load(f)
        
        self.fb = pyrebase.initialize_app(config)
        self.db = self.fb.database()

    def set_example(self, ex_id, ex):
        self.db.child('examples').child(ex_id).set(ex)

    def get_example(self, ex_id):
        return self.db.child('examples').child(ex_id).get().val()
