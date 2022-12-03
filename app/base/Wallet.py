from lib.rpc import RpcSocket
from base.RedeemScript import RedeemScript
from base.Tx_Factory import Tx_Factory

class Wallet:
    def __init__(self, wallet_name: str, username: str, password: str, url: str, port: int):
        self.rpc = RpcSocket({'wallet': wallet_name, 'username': username, 'password': password, 'url': url, 'port': port})

    def make_redeem_script(self, owner_address: str, cancel_by_time: int):
        renter_address = self.rpc.get_new_address()
        redeem_script = RedeemScript.make_from_args(renter_address, owner_address, cancel_by_time)
        return redeem_script


    def book_reservation(self, total_rent_cost: int, serial_script: str):
        all_txins = self.rpc.get_all_utxos(testnet=True)                        # find list of utxos with sufficient funds
        all_amount = self.rpc.get_total_unspent_sats()                          # get total amount in those utxos
        fee = 500                                                               # bitcoin miners fees
        change_amount = all_amount - total_rent_cost - fee                      # calculate how much is returning to renter's wallet
        tx_out_change = self.rpc.get_txout(change_amount)                       # generate p2pkh output for change

        # executed by Bitbnb app
        redeem_script = RedeemScript.make_from_serial(serial_script)                                         # build redeem_script from serial string
        transaction = Tx_Factory.make_funding(redeem_script, total_rent_cost, all_txins, tx_out_change)      # construct funding transaction
        
        #signed and sent by renter's wallet
        transaction.sign(self.rpc, testnet=True)                                # sign funding transaction
        tx_id = self.rpc.send_transaction(transaction)
        return tx_id

    def cancel_reservation(self, tx_id: str, serial_script: str):
        utxo_to_refund = self.rpc.lookup_transaction(tx_id).tx_outs[0]          # lookup p2sh utxo by txid
        utxo_amount = utxo_to_refund.amount                                     # get the amount that can be refunded
        bitcoin_miner_fee = 500                                                 # subtract out the miner fees
        refund_amount = utxo_amount - bitcoin_miner_fee                         # calculate actual refund amount
        refund_tx_out = self.rpc.get_txout(refund_amount)                       # build txout with refund amount and new address

        # executed by Bitbnb app
        redeem_script = RedeemScript.make_from_serial(serial_script)            # build redeem_script from serial string
        transaction = Tx_Factory.make_refund(tx_id, refund_tx_out)              # construct refund transaction

        # executed by renter's wallet
        address_used = redeem_script.get_refund_address(testnet=True)
        raw_serial_script = redeem_script.serialize()
        transaction.sign(self.rpc, True, address_used, raw_serial_script)        # sign p2sh input of funding of refund transaction
        tx_id = self.rpc.send_transaction(transaction)
        return tx_id

    def finalize_reservation(self, tx_id: str, serial_script: str):
        utxo_to_redeem = self.rpc.lookup_transaction(tx_id).tx_outs[0]           # lookup p2sh utxo by txid                          
        utxo_amount = utxo_to_redeem.amount                                      # get the amount that can be redeemed
        bitcoin_miner_fee = 500                                                  # subtract out the miner fees
        redeem_amount = utxo_amount - bitcoin_miner_fee                          # calculate actual redeem amount
        tx_out = self.rpc.get_txout(redeem_amount)                               # build txout with redeem amount and new address

        # executed by Bitbnb app
        redeem_script = RedeemScript.make_from_serial(serial_script)             # build redeem_script from serial string
        transaction = Tx_Factory.make_redeem(redeem_script, tx_id, tx_out)       # construct redeem transaction
        
        # executed by renter's wallet
        address_used = redeem_script.get_owner_address(testnet=True)
        raw_serial_script = redeem_script.serialize()
        transaction.sign(self.rpc, True, address_used, raw_serial_script)        # sign p2sh input of funding of refund transaction
        tx_id = self.rpc.send_transaction(transaction)
        return tx_id