from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn
from shared.Script import Script
from shared.Utility import decode_base58, little_endian_to_int, hash160

if __name__ == '__main__':   
    to_rpc = RpcSocket({'wallet': 'alice_wallet'})

    txid_with_p2sh = '086e28ec46ee19ae93c650f21f99813f69c87001e9f51a7a2c8e27e458ad6671'
    refund_addr = 'mq3QcisdaBYuKXeha7D4G8vGbcfcLSF6DG'

    refund_h160 = decode_base58(refund_addr)
    print(refund_h160.hex())

    redeem_script = Script([
        0x76,   #op_dup
        0xa9,   #op_hash160
        refund_h160,   #<pubkeyhash>
        0x88,   #op_equalverify
        0xac    #op_checksig
    ])

    tx_with_p2sh = to_rpc.lookup_transaction(txid_with_p2sh)
    utxo_to_redeem = tx_with_p2sh.tx_outs[0]
    utxo_amount = utxo_to_redeem.amount
    redeem_amount = utxo_amount - 500

    tx_in = TxIn(bytes.fromhex(txid_with_p2sh), 0)
    tx_out = to_rpc.get_txout(redeem_amount)
    transaction = Tx(1, [tx_in], [tx_out], 0, True)  
    print(transaction)
    transaction.signP2SH(to_rpc, 0, redeem_script, refund_addr)
    print(transaction)
    print(transaction.serialize().hex())
    
    tx_id = to_rpc.send_transaction(transaction)