
#!/usr/bin/env python3

import os
from pymongo import MongoClient
from urllib.parse import quote_plus

# connString = os.environ['MONGODB_CONNSTRING']
# connString = 'mongodb://bitbnb:bitpassw0rdbnb@localhost:27107'

# client = MongoClient(connString)
client = MongoClient("mongodb://localhost:27017/")
db = client.test
listings = db.listings