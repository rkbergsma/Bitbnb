from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn
from shared.Script import Script
from shared.Utility import decode_base58, little_endian_to_int, hash160

if __name__ == '__main__':   
    to_rpc = RpcSocket({'wallet': 'bob_wallet'})

    txid_with_p2sh = 'c006d8c1e834227741e5bf3d77893bc8e9016f694ccf907bee4d13371b413926'
    
    refund_addr = 'mhanwFa9pSKxcvNbaDbQDP9XmmQU9CqwvE'
    refund_h160 = decode_base58(refund_addr)

    owner_addr = 'mikwD2HAUWFnRbQGNvPfaxcq89RDY2Lr3t'
    owner_h160 = decode_base58(owner_addr)

    address_to_sign_with = owner_addr

    redeem_script = Script([
        0x76,   #op_dup
        0xa9,   #op_hash160
        refund_h160,   #<pubkeyhash>
        0x87,   #op_equal
        0x63,   #op_if
        0xac,   #op_checksig
        0x67,   #op_else
        0x76,   #op_dup
        0xa9,   #op_hash160
        owner_h160,  #<pubkeyhash>
        0x88,   #op_equalverify
        0xac,   #op_checksig
        0x68    #op_endif
    ])

    tx_with_p2sh = to_rpc.lookup_transaction(txid_with_p2sh)
    utxo_to_redeem = tx_with_p2sh.tx_outs[0]
    utxo_amount = utxo_to_redeem.amount
    redeem_amount = utxo_amount - 500

    tx_in = TxIn(bytes.fromhex(txid_with_p2sh), 0)
    tx_out = to_rpc.get_txout(redeem_amount)
    transaction = Tx(1, [tx_in], [tx_out], 0, True)  
    print(transaction)
    transaction.signP2SH(to_rpc, 0, redeem_script, address_to_sign_with)
    print(transaction)
    print(transaction.serialize().hex())
    
    tx_id = to_rpc.send_transaction(transaction)