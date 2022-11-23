import pytest
from Bitbnb.RedeemScript import RedeemScript
  
refund_addr = 'moZvNSDyo9HuLemFHdKvW9d5rTRt2QXMUy'
owner_addr = 'mvNR1qGaMR7jdmSsvFQf6nsXo7bb1ofn2M'
valid_height = 2407754
serial_script = '76a9145850a5cfd6254cd20b00493a1fd063c166043adc8763ac67034abd24b17576a914a2ec72b722b3840c7f74a38a1a7482f91e5852fa88ac68'

class TestRedeemScript:   
    def test_can_serialize(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, valid_height)
        assert serial_script == redeem_script.serialize()

    def test_can_deserialize(self):
        redeem_script = RedeemScript.make_from_serial(serial_script)
        assert serial_script == redeem_script.serialize()

    def test_can_get_renteraddr(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, valid_height)
        assert refund_addr == redeem_script.get_refund_address(testnet=True)
    
    def test_can_get_owneraddr(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, valid_height)
        assert owner_addr == redeem_script.get_owner_address(testnet=True)

    def test_can_get_locktime(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, valid_height)
        assert valid_height == redeem_script.get_owner_locktime()