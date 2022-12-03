from base.Wallet import Wallet
from shared.Script import Script
from shared.Utility import decode_base58, decode_bech32, sha256
from shared.Op import encode_num, hash160
# from lib.rpc import RpcSocket

if __name__ == '__main__':
    # to_rpc = RpcSocket({'wallet': 'bob_wallet'})
    #owner_addr = to_rpc.get_new_address()
    owner_addr = "tb1qjn82dc66rlurcq4tdjtxeuk96uk5qrfq2hjm9uvswvkjmf6fq03qzqrxgn"
    valid_height = 2408467

    wallet = Wallet('alice_wallet', 'jag2k2', 'jeff1229', '169.254.122.179', 18332)
    redeem_script = wallet.make_redeem_script(owner_addr, valid_height)
   
    serial_script = redeem_script.serialize()

    print('renter address: ' + redeem_script.get_refund_address(True))
    print('owner address: ' + owner_addr)
    print(serial_script)
    
