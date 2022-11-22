from lib.rpc import RpcSocket
from shared.Tx import Tx, TxOut
from shared.Script import Script
from shared.Utility import decode_base58, int_to_little_endian, hash160, encode_varint
from shared.Op import OP_CODE_NAMES, encode_num

if __name__ == '__main__':   
    from_rpc = RpcSocket({'wallet': 'alice_wallet'})

    refund_addr = 'mwY8KzZqft6Z7QuvEP4XpJoY2vHyUhfy33'
    owner_addr = 'n3SHuhpN4gSpn5RJvajUL4jau7d6idNNJw'
    valid_height = 2407730

    refund_h160 = decode_base58(refund_addr)
    owner_h160 = decode_base58(owner_addr)
    valid_after = encode_num(valid_height)

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
    
    serial_script = redeem_script.raw_serialize()
    hash_script = hash160(serial_script)
    p2sh_script = Script.p2sh_script(hash_script)
    print(p2sh_script)

    all_txins = from_rpc.get_all_utxos()
    all_amount = from_rpc.get_total_unspent_sats()
    fee = 500
    send_amount = 2000
    change_amount = all_amount - send_amount - fee
    tx_out = TxOut(send_amount, p2sh_script)
    tx_out_change = from_rpc.get_txout(change_amount)

    transaction = Tx(1, all_txins, [tx_out, tx_out_change], 0, True)  
    transaction.sign(from_rpc)
    print(transaction)
    print(transaction.serialize().hex())

    tx_id = from_rpc.send_transaction(transaction)