# Bitbnb

Bitbnb is a service that is aimed at facilitating Renter-Owner transactions completely on-chain. It ensures transaction security by guaranteeing:
- Owner has 100% confidence that renter is good for the money
- Renter has 100% confidence that he can cancel the reservation
- Our company takes custody of 0% of the money

## Install and Running
1. Cone the repository: `git clone git@github.com:rkbergsma/Bitbnb.git`
2. The Flask app needs the MongoDB database to be running on the backend. To start a MongoDB database instance, run `docker compose up` from the base directory. This will start a MongoDB database on localhost on port 27017.
3. To run in local mode, uncomment [dbconn.py](https://github.com/rkbergsma/Bitbnb/blob/master/app/database/dbconn.py) line 64 and comment line 65. Currently, there is a publicly available MongoDB instance running at the ngrok link provided.
4. Add your wallet information to issue transactions and to look up your rental listings.
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

