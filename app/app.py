from flask import Flask, render_template, request, url_for, flash, redirect

from database.dbconn import Dbconn
from bson.objectid import ObjectId
from base import Wallet
from datetime import datetime, timedelta
from dateutil import parser as dparser
import calendar

app = Flask(__name__)
app.config.from_envvar('APP_SETTINGS')
print("wallet name:", app.config['WALLET_NAME'])
print("rpc user:", app.config['RPC_USER'])
print("rpc pw:", app.config['RPC_PW'])
print("rpc url:", app.config['RPC_URL'])
print("rpc port:", app.config['RPC_PORT'])
print("user email:", app.config['EMAIL'])

messages = [{'title': 'Bitcoin AirBNB',
             'content': 'We are going to replace AirBNB with a better Bitcoin verison.\nUse the top menu to navigate'},
            ]

if __name__ == "__main__":
    app.run()

@app.route('/api/all_listings', methods=(['GET']))
def all_listings():
    print("***CALLING ALL LISTINGS***")
    db = Dbconn()
    all_listings = db.get_all_listings()
    db.close()
    return render_template('all_listings.html', listings = all_listings)

@app.route('/api/listing', methods=(['GET']))
def listing():
    id = request.args.get('id', '')
    db = Dbconn()
    listing = db.get_listing(id)
    bookings_for_listing = db.get_bookings_for_listing(id)
    db.close()
    return render_template('book.html', listing = listing, bookings = bookings_for_listing)


@app.route('/api/redeemable_listing', methods=(['GET']))
def redeemable_listing():
    print("***CALLING REDEEMABLE LISTING***")
    id = request.args.get('id', '')
    db = Dbconn()
    listing = db.get_listing(id)
    bookings_for_listing = db.get_bookings_for_listing(id)
    db.close()
    return render_template('view_redeemable_listing.html', listing = listing, bookings = bookings_for_listing)

@app.route('/api/redeem', methods=(['POST','GET']))
def redeem():
    print("***CALLING REDEEM***")

    if request.method == 'POST':
        booking_id = request.form['booking_id']
        listing_id = request.form['listing_id']
        db = Dbconn()
        this_booking = db.get_booking(booking_id)
        this_listing = db.get_listing(listing_id)
        bookings_for_listing = db.get_bookings_for_listing(listing_id)
        db.close()

        start_date = dparser.parse(request.form['start_date'])
        current_date = datetime.now()
        difference = start_date - current_date

        # return render_template('booking_redeemed.html', booking = this_booking)

        if difference <= timedelta(days=7): #is this redeemable yet?
            print("DIFFERENCE IS: ")
            print(difference)
            #TODO: actually redeem the script
            return render_template('booking_redeemed.html', booking = this_booking)
        else:
            print("ELSE STATEMENT. DIFFERENCE IS: ")
            print(difference)
            return render_template('view_redeemable_listing.html', listing = this_listing, bookings = bookings_for_listing)

            # return redirect(url_for('listings'))
            # print("ELSE STATEMENT. DIFFERENCE IS: ")
            # print(difference)
            # url = url_for('redeemable_listing', listing = this_listing, bookings = bookings_for_listing)
            # print("URL IS: ")
            # print(url)
            # return redirect(url)
        
@app.route('/api/book', methods=(['POST']))
def book():
    if request.method == 'POST':
        id = request.form['id'] #listing id
        db = Dbconn()
        listing = db.get_listing(id)
        bookings_for_listing = db.get_bookings_for_listing(id)
        try:
            start_date = dparser.parse(request.form['start_date'])
            end_date = dparser.parse(request.form['end_date']) + timedelta(hours=12)
        except ValueError as e:
            flash("Invalid date format!")
            return render_template('book.html', listing = listing, bookings = bookings_for_listing)
        td = end_date - start_date
        days = td.days
        epoch_time = calendar.timegm(end_date.timetuple())
        listing = db.get_listing(id)

        serial_script = gen_script(listing["btc_address"], epoch_time)
        tx_id = book_listing(days * listing["rate"], serial_script)

        booking = {
            "start_date": start_date,
            "end_date": end_date,
            "tx_id": tx_id,
            "serial_script": serial_script,
            "listing_id": ObjectId(id),
            "email": app.config['EMAIL']
        }

        booking_id = db.new_booking(booking)
        this_booking = db.get_booking(booking_id)
        db.close()

        return render_template('booking_success.html', booking = this_booking)

def gen_script(owner_address, cancel_time):
    print("Would get gen script here")
    return "abc123"

def book_listing(total_cost, cancel_time):
    print("Would book the listing here")
    return "b00kedl1stingTxId"

@app.route('/api/cancel', methods=(['POST']))
def cancel():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        db = Dbconn()
        this_booking = db.get_booking(booking_id)
        db.close()

        # TODO: Refund this TX if possible

        return render_template('cancel_refund.html', booking = this_booking)

@app.route('/api/listings', methods=(['GET']))
def listings():
    print("***CALLING MY LISTINGS***")
    db = Dbconn()
    listings = db.get_user_listings(app.config['EMAIL'])
    db.close()
    # TODO: update above to only get the user's listings
    # return render_template('all_listings.html', listings = listings)
    return render_template('my_listings.html', listings = listings)

@app.route('/api/reservations', methods=(['GET']))
def reservations():
    db = Dbconn()
    bookings = db.get_user_bookings(app.config['EMAIL'])
    db.close()
    # TODO: update above to get the user's reservations/bookings
    return render_template('bookings.html', bookings = bookings)

@app.route('/api/new', methods=('GET', 'POST'))
def new():
    # TODO: update to make form for adding a new listing
    if request.method == 'POST':
        print("IN POST OF NEW!")
        print("btc_address", request.form['btc_address'])
        print("description", request.form['description'])
        print("property_address", request.form['property_address'])
        print("rate", request.form['rate'])
        listing = {
            "btc_address": request.form['btc_address'],
            "description": request.form['description'],
            "property_address": request.form['property_address'],
            "rate": request.form['rate'],
            "email": app.config['EMAIL']
        }
        
        print("Making new listing:", listing)
        db = Dbconn()
        listing_id = db.new_listing(listing)
        this_listing = db.get_listing(listing_id)
        db.close()
        
        return render_template('listing_success.html', listing = this_listing)
    else:
        return render_template('create.html')

@app.route('/', methods=(['GET', 'POST']))
def index():
    return render_template('index.html', messages=messages)


