# Bitbnb

Bitbnb is a service that is aimed at facilitating Renter-Owner transactions completely on-chain. It ensures transaction security by guaranteeing:
- Owner has 100% confidence that renter is good for the money
- Renter has 100% confidence that he can cancel the reservation
- Our company takes custody of 0% of the money

Bitbnb achieves this by constructing a smart on-chain Bitcoin contract transaction. The difficulty in satisfying the above conditions comes in the various spend paths that must be considered. When a renter books a property, they must be able to cancel during the valid cancelation period and receive a refund. The owner of the property must be able to finalize the booking after a the cancelation period has passed. In a traditional payment system, this can only be achieved via a 3rd party. When you book through Airbnb, if you request a refund, you are relying on Airbnb to refund your money. With our contract, it is only between 2 parties and both parties have the guarantees of the contract. In Bitcoin terms, this can be thought of as a 1-of-2 multisig, with one of the parties having a timelock. Traditionally, Bitcoin transactions can be multisig, or they can have a timelock, but there is no default way to timelock one of the multisig parties. 

## Install and Running
1. Cone the repository: `git clone git@github.com:rkbergsma/Bitbnb.git`
2. The Flask app needs the MongoDB database to be running on the backend. To start a MongoDB database instance, run `docker compose up` from the base directory. This will start a MongoDB database on localhost on port 27017.
3. By default, the code will run in local mode. Alternatively, it can be modified to connect to an external MongoDB database. The commented line 65 in [dbconn.py](https://github.com/rkbergsma/Bitbnb/blob/master/app/database/dbconn.py) shows how you can connect to a MongoDB database that is running via ngrok (run `ngrok tcp 27017` and then fill in the string in `dbconn.py`).
4. Add your wallet information to send transactions and to look up your rental listings.
Open the configuration file under [config.py](https://github.com/rkbergsma/Bitbnb/blob/master/app/config.py) and replace default information in there with your own:
```
WALLET_NAME = 'insert_name_of_local_wallet_here'
RPC_USER = 'rpc_username_here'
RPC_PW = 'rpc_password_here'
RPC_URL = '127.0.0.1'
RPC_PORT = 18332
EMAIL = 'email_address_of_user'
```

Once details are filled, save the file and export an environment variable called `APP_SETTINGS` that will point to the `config.py` file mentioned above.

5. After the database and config files are set up, run the Flask app. This can be as simple as `flask run` if you have `pymongo` and `Flask` installed, or utilize a venv.
6. Visit localhost:5000 in the browser to view the home page and click through the app.

## User Workflow for Owner and Renter
The user workflow for both the owner and the renter is defined in the flow chart below. 
```

  |------------------------|    |---------------------------|    |-----------------------------------|
  | Owner Posts Properties |--->| Renter browses properties |--->| Renter selects property and dates |
  |------------------------|    |---------------------------|    |-----------------------------------|
                                                                                  |
                                                                                  |
                                                                                  |
  |------------------------|                                                      V
  | Renter can cancel for  |<--|  |---------------------------------|    |--------------------------|
  | 70% refund             |   |  | Property is reserved for renter |<---| Renter reserves property |
  |------------------------|   |--| 100% of rental price staked for |    |--------------------------|
                               |  | owner                           |
  |------------------------|   |  |---------------------------------|   
  | Reservation finalied   |<--|
  | after cancel period    |
  | expires                |
  |------------------------|
  
```
Within the app, this can be achieved by using 2 different `config.py` files. One config file can be Alice and the other can be Bob. The above workflow can be achieved by the following steps.  
To run as Alice:  
```
export APP_SETTINGS="/path/to/alice_config.py"
flask run
```

To run as Bob:
```
export APP_SETTINGS="/path/to/bob_config.py"
flask run
```

As Alice:
- Navigate to the New Listing tab and create a new listing.
- Specify the property details, including the refund cancelation policy.

As Bob:
- Navigate to All Listings, click View Listing, and book the property for a given date range.

To Cancel:  
As Bob:
- Navigate to My Reservations, press Cancel and the funds will be refunded.

To Finalize after cancel period expires:  
As Alice:
- Navigate to My Listings, click View Listing, then click Finalize on the booking that you want to finalize (note, this will be rejected if you try to finalize before the locktime is satisfied).

## The Redeeming Script for the Contract
The redeem script is defined below and can be found [here](https://github.com/rkbergsma/Bitbnb/blob/master/app/base/RedeemScript.py). If the renter provides their pubkey and the renter signs the transaction then it unlocks the funds. The else branch executes if the cancel period has expired **and** the owner provides their pubkey **and** the owner signs the transaction. If these conditions are met, the funds are unlocked.

```
redeem_script = Script([
    0x76,   #op_dup
    0xa9,   #op_hash160
    refund_h160,   #<pubkeyhash>
    0x87,   #op_equal
    0x63,   #op_if
    0xac,   #op_checksig
    0x67,   #op_else
    encoded_cancel_time,   #<can_redeem>
    0xb1,   #op_checklocktimeverify
    0x75,   #op_drop
    0x76,   #op_dup
    0xa9,   #op_hash160
    owner_h160,  #<pubkeyhash>
    0x88,   #op_equalverify
    0xac,   #op_checksig
    0x68    #op_endif
])
```
