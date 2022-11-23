from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn
from Bitbnb.Tx_Factory import Tx_Factory
from Bitbnb.RedeemScript import RedeemScript

if __name__ == '__main__':   
    txid_with_p2sh = '2356af6c295417b7ab195665d18c4e138fe648a67a510fdae7f4f7351d3023c4'
    serial_script = '76a9145850a5cfd6254cd20b00493a1fd063c166043adc8763ac67034abd24b17576a914a2ec72b722b3840c7f74a38a1a7482f91e5852fa88ac68'

    # from owner's wallet
    to_rpc = RpcSocket({'wallet': 'bob_wallet'})
    utxo_to_redeem = to_rpc.lookup_transaction(txid_with_p2sh).tx_outs[0]           # lookup utxo by txid                          
    utxo_amount = utxo_to_redeem.amount                                             # get the amount that can be redeemed
    bitcoin_miner_fee = 500                                                         # subtract out the miner fees
    redeem_amount = utxo_amount - bitcoin_miner_fee                                 # calculate actual redeem amount
    tx_out = to_rpc.get_txout(redeem_amount)                                        # build txout with redeem amount and new address

    # executed by Bitbnb app
    redeem_script = RedeemScript.make_from_serial(serial_script)                    # build redeem_script from serial string
    transaction = Tx_Factory.make_redeem(redeem_script, txid_with_p2sh, tx_out)     # construct redeem transaction
    
    # executed by renter's wallet
    address_used = redeem_script.get_owner_address(testnet=True)
    raw_serial_script = redeem_script.serialize()
    transaction.signP2SH(to_rpc, raw_serial_script, address_used)                   # sign p2sh input of funding of redeem transaction
    print(transaction)
    print(transaction.serialize().hex())
    tx_id = to_rpc.send_transaction(transaction)