from lib.rpc import RpcSocket
from shared.Tx import Tx, TxOut
from shared.Script import Script
from shared.Utility import hash160

if __name__ == '__main__':   
    from_rpc = RpcSocket({'wallet': 'alice_wallet'})

    refund_addr = 'moZvNSDyo9HuLemFHdKvW9d5rTRt2QXMUy'
    owner_addr = 'mvNR1qGaMR7jdmSsvFQf6nsXo7bb1ofn2M'
    serial_script = '76a9145850a5cfd6254cd20b00493a1fd063c166043adc8763ac67034abd24b17576a914a2ec72b722b3840c7f74a38a1a7482f91e5852fa88ac68'
    send_amount = 2000
    fee = 500

    raw_serial_script = bytes.fromhex(serial_script)
    hash_script = hash160(raw_serial_script)
    p2sh_script = Script.p2sh_script(hash_script)
    all_txins = from_rpc.get_all_utxos()
    all_amount = from_rpc.get_total_unspent_sats()
    change_amount = all_amount - send_amount - fee
    tx_out = TxOut(send_amount, p2sh_script)
    tx_out_change = from_rpc.get_txout(change_amount)
    locktime = 0
    transaction = Tx(1, all_txins, [tx_out, tx_out_change], locktime, True)  
    transaction.sign(from_rpc)

    print(transaction)
    print(transaction.serialize().hex())
    tx_id = from_rpc.send_transaction(transaction)