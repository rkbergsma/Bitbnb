from shared.Utility import hash160, h160_to_p2wpkh_address, decode_bech32

compressed_pub_key = bytes.fromhex('0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798')
h160 = hash160(compressed_pub_key)
expected_hash_mn = "751e76e8199196d454941c45d1b3a323f1433bd6"
expected_address_mn = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
expected_hash_tn = '00722cfe421d7f756d603efcbf77a7cc155d37cf'
expected_address_tn = 'tb1qqpezeljzr4lh2mtq8m7t7aa8es246d70acj379'

class TestBech32: 
    def test_make_addr_from_h160(self):
        h160 = bytes.fromhex(expected_hash_mn)
        address = h160_to_p2wpkh_address(h160, False)
        assert expected_address_mn == address

    def test_make_h160_from_addr(self):
        h160 = decode_bech32(expected_address_mn)
        assert bytes.fromhex(expected_hash_mn) == h160

    def test_made_addr_from_testnet_h160(self):
        h160 = bytes.fromhex(expected_hash_tn)
        address = h160_to_p2wpkh_address(h160, True)
        assert expected_address_tn == address

    def test_make_h160_from_testnet_addr(self):
        h160 = decode_bech32(expected_address_tn)
        assert bytes.fromhex(expected_hash_tn) == h160