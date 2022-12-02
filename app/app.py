from flask import Flask, render_template, request, url_for, flash, redirect

import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = '2fb00ba40abdb34f11c9026204333136a8afc9406e7e2f86'

messages = [{'title': 'Bitcoin AirBNB',
             'content': 'We are going to replace AirBNB with a better Bitcoin verison'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

if __name__ == "__main__":
    app.run()

@app.route('/api/all_listings', methods=(['GET']))
def all_listings():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['test']
    listings = db['listings']
    all_listings = list(listings.find({}))
    client.close()
    return render_template('all_listings.html', listings = all_listings)

@app.route('/api/listing', methods=(['GET']))
def listing():
    id = request.args.get('id', '')
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['test']
    listings = db['listings']
    listing = listings.find_one({'_id': ObjectId(id)})
    
    # TODO: get listing availability here
    
    client.close()
    print("ID:", id)

    return render_template('book.html', listing = listing)

@app.route('/api/book', methods=(['GET', 'POST']))
def book():
    if request.method == 'POST':
        id = request.form['id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        # days = end_date - start_date
        days = 2
        # TODO : actually calculate days for booking

        # TODO: book here
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client['test']
        listings = db['listings']
        listing = listings.find_one({'_id': ObjectId(id)})

        serial_script = gen_script(listing["btc_address"], 2408467)
        tx_id = book_listing(days * listing["rate"], serial_script)

        booking = {
            "start_date": start_date,
            "end_date": end_date,
            "tx_id": tx_id,
            "serial_script": serial_script,
            "listing_id": ObjectId(id),
            "user": "SuperTestNet"
        }

        bookings = db['bookings']
        this_booking = bookings.insert_one(booking)

        client.close()
    else:
        pass
    # client = pymongo.MongoClient("mongodb://localhost:27017/")
    # db = client['test']
    # listings = db['listings']
    # listing = list(listings.find_one({'_id': ObjectId(id)}))[0]
    # client.close()

    # booking = {"start_date": start_date, "end_date": end_date, "tx_id": "tx_id here"}
    return render_template('success.html', booking = this_booking)

def gen_script(owner_address, cancel_time):
    print("Would get gen script here")
    return "abc123"

def book_listing(total_cost, cancel_time):
    print("Would book the listing here")
    return "b00kedl1stingTxId"

@app.route('/api/listings', methods=(['GET']))
def listings():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['test']
    listings = db['listings']
    doc = listings.find_one()
    listings = [doc]
    client.close()
    # get personal listings here
    return render_template('all_listings.html', listings = listings)

@app.route('/api/reservations', methods=(['GET']))
def reservations():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['test']
    listings = db['listings']
    doc = listings.find_one()
    listings = [doc]
    client.close()
    # get personal listings here
    return render_template('all_listings.html', listings = listings)

@app.route('/api/new', methods=('GET', 'POST'))
def new():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        print("REQUEST:", request)
        return redirect(url_for('index'))

        # if not title:
        #     flash('Title is required!')
        # elif not content:
        #     flash('Content is required!')
        # else:
        #     messages.append({'title': title, 'content': content})
        #     return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/', methods=(['GET', 'POST']))
def index():
    return render_template('index.html', messages=messages)


