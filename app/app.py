from flask import Flask, render_template, request, url_for, flash, redirect

from database.dbconn import Dbconn
from bson.objectid import ObjectId
from base.Wallet import Wallet
from base.RedeemScript import RedeemScript
from datetime import datetime, timedelta
from dateutil import parser as dparser
from lib.rpc import RpcSocket
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

        redeem_script = RedeemScript.make_from_serial(this_booking['serial_script'])
        epoch_locktime = datetime.fromtimestamp(int(redeem_script.get_owner_locktime()))
        if datetime.now() < epoch_locktime:
            flash("Locktime has not expired yet!")
            return render_template('view_redeemable_listing.html', listing = this_listing, bookings = bookings_for_listing)
        
        try:
            wallet = Wallet(app.config['WALLET_NAME'], app.config['RPC_USER'], app.config['RPC_PW'], app.config['RPC_URL'], app.config['RPC_PORT'])
            finalized_tx = wallet.finalize_reservation(this_booking['tx_id'], this_booking['serial_script'])
            print(finalized_tx)
            finalized_confirmation = {
                "start_date": this_booking['start_date'],
                "end_date": this_booking['end_date'],
                "tx_id": finalized_tx,
                "_id": this_booking['_id']
            }
            return render_template('booking_redeemed.html', booking = finalized_confirmation)
        except Exception as e:
            flash("Transaction failed due to lock time: " + str(e))
            print(e)
            return render_template('view_redeemable_listing.html', listing = this_listing, bookings = bookings_for_listing)
        
        # start_date = dparser.parse(request.form['start_date'])
        # current_date = datetime.now()
        # difference = start_date - current_date
        # # return render_template('booking_redeemed.html', booking = this_booking)

        # if difference <= timedelta(days=7): #is this redeemable yet?
        #     print("DIFFERENCE IS: ")
        #     print(difference)
        #     #TODO: actually redeem the script
        #     return render_template('booking_redeemed.html', booking = this_booking)
        # else:
        #     print("ELSE STATEMENT. DIFFERENCE IS: ")
        #     print(difference)
        #     return render_template('view_redeemable_listing.html', listing = this_listing, bookings = bookings_for_listing)

        #     # return redirect(url_for('listings'))
        #     # print("ELSE STATEMENT. DIFFERENCE IS: ")
        #     # print(difference)
        #     # url = url_for('redeemable_listing', listing = this_listing, bookings = bookings_for_listing)
        #     # print("URL IS: ")
        #     # print(url)
        #     # return redirect(url)

class BookingDateError(Exception):
    """Exception raised for errors in the booking date.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Invalid booking date"):
        self.message = message
        super().__init__(self.message)

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
            if end_date < start_date:
                raise BookingDateError("End date before start date!")
            for booking in bookings_for_listing:
                if start_date > booking['start_date'] and start_date < booking['end_date']:
                    raise BookingDateError("Booking already reserved at this time.")
                if end_date > booking['start_date'] and end_date < booking['end_date']:
                    raise BookingDateError("Booking already reserved at this time.")
        except ValueError as e:
            flash("Invalid date format!")
            return render_template('book.html', listing = listing, bookings = bookings_for_listing)
        except BookingDateError as e:
            flash(str(e))
            return render_template('book.html', listing = listing, bookings = bookings_for_listing)
        td = end_date - start_date
        days = td.days
        cancel_epoch_date = start_date - timedelta(days = listing['cancel_days'])
        epoch_time = calendar.timegm(cancel_epoch_date.timetuple())
        listing = db.get_listing(id)
        booking_amount = int(days * int(listing['rate']))

        try:
            wallet = Wallet(app.config['WALLET_NAME'], app.config['RPC_USER'], app.config['RPC_PW'], app.config['RPC_URL'], app.config['RPC_PORT'])
            serial_script = wallet.make_redeem_script(listing["btc_address"], epoch_time)
            serial_script = serial_script.serialize()
            print("Serial script:", serial_script)
            tx_id = wallet.book_reservation(booking_amount, serial_script)
            print("TX ID:", tx_id)
        except Exception as e:
            print(e)
            flash(str(e))
            return render_template('booking_success.html', booking = this_booking)

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
        try:
            wallet = Wallet(app.config['WALLET_NAME'], app.config['RPC_USER'], app.config['RPC_PW'], app.config['RPC_URL'], app.config['RPC_PORT'])
            cancel_tx = wallet.cancel_reservation(this_booking['tx_id'], this_booking['serial_script'])
            print("Cancel tx id:", cancel_tx)
            cancel_confirmation = {
                "start_date": this_booking['start_date'],
                "end_date": this_booking['end_date'],
                "tx_id": cancel_tx,
                "_id": this_booking['_id']
            }
            return render_template('cancel_refund.html', booking = cancel_confirmation)
        except Exception as e:
            flash(str(e))
            db = Dbconn()
            bookings = db.get_user_bookings(app.config['EMAIL'])
            db.close()  
            return render_template('bookings.html', bookings = bookings)

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
        try:
            rpc = RpcSocket({'wallet': app.config['WALLET_NAME'], 'username': app.config['RPC_USER'], 
            'password': app.config['RPC_PW'], 'url': app.config['RPC_URL'], 'port': app.config['RPC_PORT']})
            btc_address = rpc.get_new_address()
        except Exception as e:
            print(e)
            flash(str(e))
            return render_template('create.html')
        try:
            cancel_days = int(request.form['cancel_days'])
        except ValueError as e:
            cancel_days = 7
        print("btc_address", btc_address)
        print("description", request.form['description'])
        print("property_address", request.form['property_address'])
        print("rate", request.form['rate'])
        print("cancel days", cancel_days)
        listing = {
            "btc_address": btc_address,
            "description": request.form['description'],
            "property_address": request.form['property_address'],
            "rate": request.form['rate'],
            "email": app.config['EMAIL'],
            "cancel_days": cancel_days
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


