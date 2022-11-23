from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn
from Bitbnb.Tx_Factory import Tx_Factory
from Bitbnb.RedeemScript import RedeemScript

if __name__ == '__main__':   
    # generated by Bitbnb app when user click's "reserve"
    txid_with_p2sh = 'dac6539c316d00ee516de294c4c4bbae7616aca8e6d7f020da4b3b4ad3567737'
    serial_script = '76a9145850a5cfd6254cd20b00493a1fd063c166043adc8763ac67034abd24b17576a914a2ec72b722b3840c7f74a38a1a7482f91e5852fa88ac68'

    # from renter's wallet
    to_rpc = RpcSocket({'wallet': 'alice_wallet'})
    utxo_to_refund = to_rpc.lookup_transaction(txid_with_p2sh).tx_outs[0]   # lookup utxo by txid
    utxo_amount = utxo_to_refund.amount                                     # get the amount that can be refunded
    bitcoin_miner_fee = 500                                                 # subtract out the miner fees
    refund_amount = utxo_amount - bitcoin_miner_fee                         # calculate actual refund amount
    refund_tx_out = to_rpc.get_txout(refund_amount)                         # build txout with refund amount and new address

    # executed by Bitbnb app
    redeem_script = RedeemScript.make_from_serial(serial_script)            # build redeem_script from serial string
    transaction = Tx_Factory.make_refund(txid_with_p2sh, refund_tx_out)     # construct refund transaction

    # executed by renter's wallet
    address_used = redeem_script.get_refund_address(testnet=True)
    raw_serial_script = redeem_script.serialize()
    transaction.signP2SH(to_rpc, raw_serial_script, address_used)           # sign p2sh input of funding of refund transaction
    print(transaction)
    print(transaction.serialize().hex())
    tx_id = to_rpc.send_transaction(transaction)
