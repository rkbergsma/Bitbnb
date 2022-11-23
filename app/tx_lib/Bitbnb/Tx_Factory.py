from io import BytesIO
from shared.Tx import Tx, TxOut, TxIn
from shared.Script import Script
from Bitbnb import RedeemScript
from typing import List

class Tx_Factory:
    @classmethod
    def make_funding(cls, redeem_script: RedeemScript, total_rent_price_sats: int, funding_tx_ins: List[TxIn], change_tx_out: TxOut):
        hash_script = bytes.fromhex(redeem_script.hash160())
        p2sh_script = Script.p2sh_script(hash_script)
        tx_out = TxOut(total_rent_price_sats, p2sh_script)
        locktime = 0
        return Tx(1, funding_tx_ins, [tx_out, change_tx_out], locktime, True) 

    def make_refund(self):
        return False

    def make_redeem(self):
        return False