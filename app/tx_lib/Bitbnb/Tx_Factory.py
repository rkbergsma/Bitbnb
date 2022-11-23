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

    @classmethod
    def make_refund(cls, txid_to_refund: str, refund_txout: TxOut):   
        tx_out_index_to_refund = 0
        tx_in = TxIn(bytes.fromhex(txid_to_refund), tx_out_index_to_refund)
        locktime = 0
        return Tx(1, [tx_in], [refund_txout], locktime, True) 

    @classmethod
    def make_redeem(cls, redeem_script: RedeemScript, txid_to_redeem: str, redeem_txout: TxOut):
        tx_out_index_to_redeem = 0
        tx_in = TxIn(bytes.fromhex(txid_to_redeem), tx_out_index_to_redeem)
        locktime = redeem_script.get_owner_locktime()
        return Tx(1, [tx_in], [redeem_txout], locktime, True)  
