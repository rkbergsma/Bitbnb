from lib.rpc import RpcSocket
from shared.Tx import Tx, TxOut
from shared.Script import Script
from shared.Utility import decode_base58, little_endian_to_int, hash160
from shared.Op import OP_CODE_NAMES

if __name__ == '__main__':   
    from_rpc = RpcSocket({'wallet': 'alice_wallet'})

    refund_addr = 'mhanwFa9pSKxcvNbaDbQDP9XmmQU9CqwvE'
    refund_h160 = decode_base58(refund_addr)

    owner_addr = 'mikwD2HAUWFnRbQGNvPfaxcq89RDY2Lr3t'
    owner_h160 = decode_base58(owner_addr)

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