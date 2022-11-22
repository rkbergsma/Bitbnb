from lib.rpc import RpcSocket
from shared.Tx import Tx, TxIn
from shared.Script import Script
from shared.Utility import decode_base58, int_to_little_endian, hash160, encode_varint
from shared.Op import encode_num

if __name__ == '__main__':   
    to_rpc = RpcSocket({'wallet': 'bob_wallet'})

    txid_with_p2sh = '056dd7c43e8d8f17bc4ff66f7960c4330f5831548d584d04c3c68ecbbf5fcdf1'
    
    refund_addr = 'mwY8KzZqft6Z7QuvEP4XpJoY2vHyUhfy33'
    owner_addr = 'n3SHuhpN4gSpn5RJvajUL4jau7d6idNNJw'
    valid_height = 2407730
    locktime = 2407730

    refund_h160 = decode_base58(refund_addr)
    owner_h160 = decode_base58(owner_addr)
    valid_after = encode_num(valid_height)

    print(refund_h160.hex())
    print(owner_h160.hex())
    print(valid_after.hex())

    address_to_sign_with = owner_addr

    redeem_script = Script([
        0x76,   #op_dup
        0xa9,   #op_hash160
        refund_h160,   #<pubkeyhash>
        0x87,   #op_equal
        0x63,   #op_if
        0xac,   #op_checksig
        0x67,   #op_else
        valid_after,   #<can_redeem>
        0xb1,   #op_checklocktimeverify
        0x75,   #op_drop
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
    transaction = Tx(1, [tx_in], [tx_out], locktime, True)  
    transaction.signP2SH(to_rpc, 0, redeem_script, address_to_sign_with)
    print(transaction)
    print(transaction.serialize().hex())
    
    tx_id = to_rpc.send_transaction(transaction)