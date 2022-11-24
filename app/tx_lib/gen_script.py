from lib.rpc import RpcSocket
from shared.Utility import decode_base58, decode_bech32
from shared.Op import encode_num
from shared.Script import Script

if __name__ == '__main__':
    legacy = False
    from_rpc = RpcSocket({'wallet': 'alice_wallet'})
    to_rpc = RpcSocket({'wallet': 'bob_wallet'})

    refund_addr = from_rpc.get_new_address(legacy)
    owner_addr = to_rpc.get_new_address(legacy)
    valid_height = 2407754

    if legacy == False:
        refund_h160 = decode_bech32(refund_addr)
        owner_h160 = decode_bech32(owner_addr)
    else:
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
    
    serial_script = redeem_script.raw_serialize().hex()

    print('renter address: ' + refund_addr)
    print('owner address: ' + owner_addr)
    print(serial_script)
    
