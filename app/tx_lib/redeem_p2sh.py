from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn

if __name__ == '__main__':   
    to_rpc = RpcSocket({'wallet': 'bob_wallet'})

    txid_with_p2sh = '215d88e19811aefb0d476207154a662c6dec597cca69c7a4a57a85f5f76f2644'
    address = 'mvNR1qGaMR7jdmSsvFQf6nsXo7bb1ofn2M'
    serial_script = '76a9145850a5cfd6254cd20b00493a1fd063c166043adc8763ac67034abd24b17576a914a2ec72b722b3840c7f74a38a1a7482f91e5852fa88ac68'
    locktime = 2407754
    fee = 500

    raw_serial_script = bytes.fromhex(serial_script)
    tx_with_p2sh = to_rpc.lookup_transaction(txid_with_p2sh)
    utxo_to_redeem = tx_with_p2sh.tx_outs[0]
    utxo_amount = utxo_to_redeem.amount
    redeem_amount = utxo_amount - fee
    tx_out_index_to_redeem = 0
    tx_in = TxIn(bytes.fromhex(txid_with_p2sh), tx_out_index_to_redeem)
    tx_out = to_rpc.get_txout(redeem_amount)
    transaction = Tx(1, [tx_in], [tx_out], locktime, True)  
    transaction.signP2SH(to_rpc, 0, raw_serial_script, address)
    
    print(transaction)
    print(transaction.serialize().hex())
    tx_id = to_rpc.send_transaction(transaction)