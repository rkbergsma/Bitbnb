from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn

if __name__ == '__main__':   
    to_rpc = RpcSocket({'wallet': 'alice_wallet'})

    txid_with_p2sh = 'bfc1cbaa430691af6ac342f41cb2ac6895a86224bdca3f906d45386f11f49f0d'
    address = 'n1mCUKwJtpJXCQ3uMhthpzQ2m8M83f89xZ'
    serial_script = '76a914de142c71a4d9069f04b26a1ac26b7fd07aae94ba8763ac670332bd24b17576a914bedb947f5594a858531ea3cab0517a330c1fb14188ac68'

    raw_serial_script = bytes.fromhex(serial_script)
    tx_with_p2sh = to_rpc.lookup_transaction(txid_with_p2sh)
    utxo_to_redeem = tx_with_p2sh.tx_outs[0]
    utxo_amount = utxo_to_redeem.amount
    redeem_amount = utxo_amount - 500
    tx_out_index_to_refund = 0
    tx_in = TxIn(bytes.fromhex(txid_with_p2sh), tx_out_index_to_refund)
    tx_out = to_rpc.get_txout(redeem_amount)
    locktime = 0
    transaction = Tx(1, [tx_in], [tx_out], locktime, True)  
    input_index_to_sign = 0
    transaction.signP2SH(to_rpc, input_index_to_sign, raw_serial_script, address)
    
    print(transaction)
    print(transaction.serialize().hex())
    tx_id = to_rpc.send_transaction(transaction)