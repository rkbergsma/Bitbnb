import pymongo
from typing import Callable
from functools import wraps
from datetime import datetime, timedelta, date
from bson.objectid import ObjectId

def _check_connected(func: Callable):
    """
    decorator for functions which require an active connection to operate
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.connected():
            print("Database not connected, reconnecting")
            self.open()
        return func(self, *args, **kwargs)
    return wrapper

class Dbconn(object):
    """
    Encapsulates our database connection
    """
    def __init__(self, database: str = "localhost", port: int = 27017) -> None:
        if not database:
            raise Exception("No database provided!")
        self.database = database
        self.port = port
        self.client = None
        self.db = None
        self.listings = None
        self.bookings = None
        self._connected = None

    def __str__(self):
        return f'Connected to {self.database}'

    def __eq__(self, other):
        return (self is other) or (
            self.database == getattr(other, 'database', None)
        )

    def __hash__(self):
        return hash(self.database)
    
    def connected(self):
        """
        returns true if the connection is active
        """
        if self._connected is None:
            return False
        try:
            self.client.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            return False
        return True

    def open(self):
        """
        open a connection to the database
        """
        if self.connected():
            print("Already connected to database")
        try:
            # self.client = pymongo.MongoClient("mongodb://" + self.database + ":" + str(self.port) + "/")
            self.client = pymongo.MongoClient("mongodb://4.tcp.ngrok.io:12267")
            self.db = self.client.test
            self.listings = self.db.listings
            self.bookings = self.db.bookings
            self._connected = True
            print("Successfully connected to database")
        except pymongo.errors.ConnectionFailure as e:
            raise Exception("Error connecting to database")
    
    def close(self):
        """
        closes the connection
        """
        try:
            self.client.close()
        finally:
            self._connected = None

    # Listings:
    @_check_connected
    def get_listing(self, listing_id):
        if isinstance(listing_id, str):
            listing_id = ObjectId(listing_id)
        return self.listings.find_one({'_id': listing_id})

    @_check_connected
    def get_all_listings(self):
        return list(self.listings.find({}))

    @_check_connected
    def get_user_listings(self, user_email):
        return list(self.listings.find({'email': user_email}))
    
    @_check_connected
    def new_listing(self, listing):
        result = self.listings.insert_one(listing)
        return result.inserted_id

    # Bookings:
    @_check_connected
    def get_bookings_for_listing(self, listing_id):
        if isinstance(listing_id, str):
            listing_id = ObjectId(listing_id)
        return list(self.bookings.find({'listing_id': listing_id}))

    @_check_connected
    def get_booking(self, booking_id):
        if isinstance(booking_id, str):
            booking_id = ObjectId(booking_id)
        return self.bookings.find_one({'_id': booking_id})

    @_check_connected
    def get_user_bookings(self, user_email):
        return list(self.bookings.find({'email': user_email}))

    @_check_connected
    def new_booking(self, booking):
        result = self.bookings.insert_one(booking)
        return result.inserted_id