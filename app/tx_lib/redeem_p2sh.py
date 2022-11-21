from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn
from shared.Script import Script
from shared.Utility import decode_base58, little_endian_to_int, hash160

if __name__ == '__main__':   
    to_rpc = RpcSocket({'wallet': 'bob_wallet'})

    redeem_script = Script([0x76, 0x93, 0x93, 0x57, 0x87])
    script_sig = Script([0x53, 0x52, redeem_script.raw_serialize()])

    txid_with_p2sh = '8a6f86f0101c282a5665545d2f96673a67a3569031843e2e70527763bb825940'

    tx_with_p2sh = to_rpc.lookup_transaction(txid_with_p2sh)
    utxo_to_redeem = tx_with_p2sh.tx_outs[0]
    utxo_amount = utxo_to_redeem.amount
    redeem_amount = utxo_amount - 500

    tx_in = TxIn(bytes.fromhex(txid_with_p2sh), 0, script_sig)
    tx_out = to_rpc.get_txout(redeem_amount)
    transaction = Tx(1, [tx_in], [tx_out], 0, True)  
    print(transaction)
    print(transaction.serialize().hex())
    
    tx_id = to_rpc.send_transaction(transaction)