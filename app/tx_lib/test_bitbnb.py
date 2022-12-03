
from base.RedeemScript import RedeemScript
  
refund_addr = 'tb1qm8t5e4eu9r8h6p3ydj9sx9lyy2x3dxmwzrr83k'
owner_addr = 'tb1qmup759murt7rgvz9gwcn4kusmzz20yqluqq8m5'
cancel_by_time = 2408467
serial_script = '76a914d9d74cd73c28cf7d06246c8b0317e4228d169b6e8763ac670313c024b17576a914df03ea177c1afc34304543b13adb90d884a7901f88ac68'
script_h160 = 'e2b7274327d27d0b24ca2c7cd024b8cadb5da113'
script_sha256 = '7bc02035b928d1f7d1fe987c154cc4d20200594f6cd0acfb75c2c7e9d609bffd'

class TestRedeemScript:   
    def test_can_serialize(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, cancel_by_time)
        assert serial_script == redeem_script.serialize()

    def test_can_deserialize(self):
        redeem_script = RedeemScript.make_from_serial(serial_script)
        assert serial_script == redeem_script.serialize()

    def test_can_get_renteraddr(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, cancel_by_time)
        assert refund_addr == redeem_script.get_refund_address(testnet=True)
    
    def test_can_get_owneraddr(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, cancel_by_time)
        assert owner_addr == redeem_script.get_owner_address(testnet=True)

    def test_can_get_locktime(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, cancel_by_time)
        assert cancel_by_time == redeem_script.get_owner_locktime()
    
    def test_can_get_h160(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, cancel_by_time)
        assert script_h160 == redeem_script.hash160()

    def test_can_geth256(self):
        redeem_script = RedeemScript.make_from_args(refund_addr, owner_addr, cancel_by_time)
        assert script_sha256 == redeem_script.sha256()