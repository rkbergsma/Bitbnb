from shared.Utility import decode_base58, encode_base58, hash160
from shared.PrivateKey import PrivateKey
from lib.helper import decode_address

if __name__ == '__main__':  
    test_addr = 'moLieZyT7DhBwy8DRBe5njk42aE87JozRE'
    decoded_addr = decode_base58(test_addr).hex()
    # print(decoded_addr)



    refund_addr = 'mq3QcisdaBYuKXeha7D4G8vGbcfcLSF6DG'
    refund_priv_key = 'cUjfPpE5Wxh15dB3k2WWXi4s1JDR8PbYSGEoG2hEZ1NiyWN9E3kM'
    private_key = decode_address(refund_priv_key)
    print(private_key)
    secret_int = int(private_key,16)
    private_key = PrivateKey(secret_int)
    print(private_key.hex())

    pub_key = private_key.public_key.sec()
    print(pub_key)

    h160_pubkey = hash160(pub_key)
    print(h160_pubkey.hex())
    print(decode_base58(refund_addr).hex())


    owner_addr = 'mk1XpL5HqqDCmcasJYQ5SqPGwZs8Y2pBtT'