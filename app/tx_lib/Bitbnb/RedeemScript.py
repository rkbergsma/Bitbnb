from shared.Script import Script
from io import BytesIO
from shared.Utility import h160_to_p2pkh_address, decode_base58, encode_varint
from shared.Op import encode_num, decode_num, hash160

class RedeemScript:
    def __init__(self, redeem_script:Script):
        self.redeem_script = redeem_script

    @classmethod        
    def make_from_args(cls, refund_address: str, owner_address: str, cancel_time: int):
        refund_h160 = decode_base58(refund_address)
        owner_h160 = decode_base58(owner_address)
        encoded_cancel_time = encode_num(cancel_time)

        redeem_script = Script([
            0x76,   #op_dup
            0xa9,   #op_hash160
            refund_h160,   #<pubkeyhash>
            0x87,   #op_equal
            0x63,   #op_if
            0xac,   #op_checksig
            0x67,   #op_else
            encoded_cancel_time,   #<can_redeem>
            0xb1,   #op_checklocktimeverify
            0x75,   #op_drop
            0x76,   #op_dup
            0xa9,   #op_hash160
            owner_h160,  #<pubkeyhash>
            0x88,   #op_equalverify
            0xac,   #op_checksig
            0x68    #op_endif
        ])
        return cls(redeem_script)

    @classmethod
    def make_from_serial(cls, serial_redeem_script: str):
        serial_script_bytes = bytes.fromhex(serial_redeem_script)
        total = len(serial_script_bytes)
        encoded_serial_script =  encode_varint(total) + serial_script_bytes
        redeem_script = Script.parse(BytesIO(encoded_serial_script))
        return cls(redeem_script)

    def get_refund_address(self, testnet=False) -> str:
        refund_h160 = self.redeem_script.cmds[2]
        return h160_to_p2pkh_address(refund_h160, testnet)

    def get_owner_address(self, testnet=False) -> str:
        owner_h160 = self.redeem_script.cmds[12]
        return h160_to_p2pkh_address(owner_h160, testnet)

    def get_owner_locktime(self) -> str:
        encoded_locktime = self.redeem_script.cmds[7]
        return decode_num(encoded_locktime)

    def serialize(self) -> str:
        return self.redeem_script.raw_serialize().hex()

    def hash160(self) -> str:
        serial_script = bytes.fromhex(self.serialize())
        return hash160(serial_script).hex()
    
