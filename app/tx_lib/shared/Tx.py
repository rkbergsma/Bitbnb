from io import BytesIO
from shared.PrivateKey import PrivateKey
from shared.Utility import hash256, int_to_little_endian, little_endian_to_int, read_varint, encode_varint, h160_to_p2pkh_address, h160_to_p2wpkh_address
from shared.Script import Script, p2pkh_script

SIGHASH_ALL = 1

class Tx:
    command = b'tx'

    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False, segwit=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet
        self.segwit = segwit
        self._hash_prevouts = None
        self._hash_sequence = None
        self._hash_outputs = None
    
    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime,
        )
    
    def id(self): 
        return self.hash().hex()

    def hash(self):
        return hash256(self.serialize_legacy())[::-1]

    def serialize(self):
        if self.segwit:
            return self.serialize_segwit()
        else:
            return self.serialize_legacy()
    
    def serialize_segwit(self):
        result = int_to_little_endian(self.version, 4)
        result += b'\x00\x01'                                   # Add the segwit marker and flag
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        for tx_in in self.tx_ins:                               # The serialize the witness field
            result += int_to_little_endian(len(tx_in.witness), 1)
            for item in tx_in.witness:
                if type(item) == int:
                    result += int_to_little_endian(item, 1)     # The item is a command so encode it as a single byte
                else:
                    result += encode_varint(len(item)) + item   # The item is a byte stream so prepend he length to it
        result += int_to_little_endian(self.locktime, 4)
        return result

    def serialize_legacy(self):
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result
    
    def fee(self, testnet=False):
        value_of_inputs = 0
        for tx_in in self.tx_ins:
            value_of_inputs += tx_in.value
        value_of_outputs = 0
        for tx_out in self.tx_outs:
            value_of_outputs += tx_out.amount
        return value_of_inputs - value_of_outputs

    def sig_hash(self, rpc, input_index, raw_serial_script=None):
        modified_tx = int_to_little_endian(self.version, 4)
        modified_tx += encode_varint(len(self.tx_ins))
        # empty ScriptSig from all inputs.  Replace ScriptSig with ScriptPubKey for just input being signed
        for i, tx_in in enumerate(self.tx_ins): 
            if i == input_index:
                if raw_serial_script:
                    total = len(raw_serial_script)
                    encoded_serial_script =  encode_varint(total) + raw_serial_script
                    script_sig = Script.parse(BytesIO(encoded_serial_script))
                else:
                    script_sig = tx_in.lookup_script_pubkey(rpc, self.testnet)
            else:
                script_sig = None
            modified_tx += TxIn(tx_in.prev_tx, tx_in.prev_index, script_sig, tx_in.sequence).serialize()
        modified_tx += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            modified_tx += tx_out.serialize()
        modified_tx += int_to_little_endian(self.locktime, 4)
        # append hash type
        modified_tx += int_to_little_endian(SIGHASH_ALL, 4)
        h256 = hash256(modified_tx)
        return int.from_bytes(h256, 'big')

    def sig_hash_bip143(self, rpc, input_index, redeem_script=None, witness_script=None):
        '''Returns the integer representation of the hash that needs to get signed for index input_index'''
        tx_in = self.tx_ins[input_index]
        # per BIP143 spec
        s = int_to_little_endian(self.version, 4)
        s += self.hash_prevouts() + self.hash_sequence()
        s += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
        if witness_script:
            script_code = witness_script.serialize()
        elif redeem_script:
            script_code = p2pkh_script(redeem_script.cmds[1]).serialize()
        else:
            script_sig = tx_in.lookup_script_pubkey(rpc, self.testnet)
            script_code = p2pkh_script(script_sig.cmds[1]).serialize()
        s += script_code
        s += int_to_little_endian(tx_in.lookup_value(rpc), 8)
        s += int_to_little_endian(tx_in.sequence, 4)
        s += self.hash_outputs()
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)
        return int.from_bytes(hash256(s), 'big')

    def hash_prevouts(self):
        if self._hash_prevouts is None:
            all_prevouts = b''
            all_sequence = b''
            for tx_in in self.tx_ins:
                all_prevouts += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
                all_sequence += int_to_little_endian(tx_in.sequence, 4)
            self._hash_prevouts = hash256(all_prevouts)
            self._hash_sequence = hash256(all_sequence)
        return self._hash_prevouts

    def hash_sequence(self):
        if self._hash_sequence is None:
            self.hash_prevouts()  # this should calculate self._hash_prevouts
        return self._hash_sequence

    def hash_outputs(self):
        if self._hash_outputs is None:
            all_outputs = b''
            for tx_out in self.tx_outs:
                all_outputs += tx_out.serialize()
            self._hash_outputs = hash256(all_outputs)
        return self._hash_outputs

    def verify_input(self, rpc, input_index):
        tx_in = self.tx_ins[input_index]
        script_pubkey = tx_in.lookup_script_pubkey(rpc, self.testnet)   # fetch for the pubkey of the prev transaction
        if script_pubkey.is_p2sh():
            cmd = tx_in.script_sig.cmds[-1]                             # the last command has to be the redeem script to trigger
            raw_redeem = encode_varint(len(cmd)) + cmd;
            redeem_script = Script.parse(BytesIO(raw_redeem))           # the RedeemScript might be p2wpkh or p2wsh
            if redeem_script.is_p2wpkh():
                z = self.sig_hash_bip143(input_index, redeem_script)
                witness = tx_in.witness
            else:
                z = self.sig_hash(rpc, input_index, redeem_script)
                witness = None
        else:
            if script_pubkey.is_p2wpkh():
                z = self.sig_hash_bip143(rpc, input_index)
                witness = tx_in.witness
            else:
                z = self.sig_hash(rpc, input_index)
                witness = None    
        combined_script = tx_in.script_sig + script_pubkey
        return combined_script.evaluate(z, witness)

    def verify(self):
        if self.fee() < 0:
            return False
        for i in range(len(self.tx_ins)):
            if not self.verify_input(i):
                return False
        return True

    def sign(self, rpc, testnet=False, sh_address=None):
        for i in range(len(self.tx_ins)):
            script_pubkey = self.tx_ins[i].lookup_script_pubkey(rpc, testnet)
            if script_pubkey.is_p2pkh():
                h160 = script_pubkey.cmds[2]
                address = h160_to_p2pkh_address(h160, testnet)
            elif script_pubkey.is_p2wpkh():
                h160 = script_pubkey.cmds[1]
                address = h160_to_p2wpkh_address(h160, testnet)
            elif script_pubkey.is_p2sh():
                address = sh_address
            privateKey = rpc.get_private_key(address)
            self.sign_input(rpc, i, privateKey)
        return True

    def signP2SH(self, rpc, serial_redeem_script: str, address_in_p2sh: str, testnet=False):
        serial_script_bytes = bytes.fromhex(serial_redeem_script)
        privateKey = rpc.get_private_key(address_in_p2sh)
        self.sign_input(rpc, 0, privateKey, serial_script_bytes)
        return True

    def sign_input(self, rpc, input_index, private_key, raw_serial_script=None):
        tx_in = self.tx_ins[input_index]
        script_pubkey = tx_in.lookup_script_pubkey(rpc, self.testnet)
        if script_pubkey.is_p2sh():
            script_sig = Script([sig, sec, raw_serial_script])
        elif script_pubkey.is_p2pkh():
            z = self.sig_hash(rpc, input_index, raw_serial_script)
            der = private_key.sign(z).der()                                             # create the signature
            sig = der + SIGHASH_ALL.to_bytes(1, 'big')
            sec = private_key.public_key.sec()
            script_sig = Script([sig, sec])
        elif script_pubkey.is_p2wpkh():
            z = self.sig_hash_bip143(rpc, input_index)
            der = private_key.sign(z).der()                                             # create the signature
            sig = der + SIGHASH_ALL.to_bytes(1, 'big')
            sec = private_key.public_key.sec()
            script_sig = Script([])
            self.tx_ins[input_index].witness = [sig, sec]
        self.tx_ins[input_index].script_sig = script_sig                           # sign the transaction's input
        return self.verify_input(rpc, input_index)

    @classmethod
    def parse(cls, stream, testnet=False):
        stream.read(4)                          # read off the first 4 bytes (version) so we can look at the fifth
        if stream.read(1) == b'\x00':           # if fifth bytes is 0, this is a segwit transaction
            parse_method = cls.parse_segwit
        else:
            parse_method = cls.parse_legacy
        stream.seek(-5,1)                       # reset the stream
        return parse_method(stream, testnet=testnet)

    @classmethod
    def parse_segwit(cls, stream, testnet=False):
        version = little_endian_to_int(stream.read(4))
        marker_flag = stream.read(2)            # read marker and flag 
        if marker_flag != b'\x00\x01':          
            raise RuntimeError("The maker and flag {} do not indicate this is a segwit transaction".format(marker_flag))
        num_inputs = read_varint(stream)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(stream))
        outputs = []
        num_outputs = read_varint(stream)
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(stream))
        for tx_in in inputs:                    # assume there is a set of witness items for each input I guess?
            num_items = read_varint(stream)
            items = []
            for _ in range(num_items):
                item_len = read_varint(stream)
                if item_len == 0:
                    items.append(0)
                else:
                    items.append(stream.read(item_len))
            tx_in.witness = items               # yup you can add properties to classes like this apparently.  
        locktime = little_endian_to_int(stream.read(4))
        return cls(version, inputs, outputs, locktime, testnet=testnet, segwit=True)

    @classmethod
    def parse_legacy(cls, stream, testnet=False):
        version = little_endian_to_int(stream.read(4))
        num_inputs = read_varint(stream)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(stream))
        outputs = []
        num_outputs = read_varint(stream)
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(stream))
        locktime = little_endian_to_int(stream.read(4))
        return cls(version, inputs, outputs, locktime, testnet=testnet)


class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xfffffffe):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        return '{}:{}:{}'.format(self.prev_tx.hex(), self.prev_index, self.script_sig)

    def setPrevTxInfo(self, private_key, script_pubKey, amount):
        self.private_key = private_key
        self.script_pubkey = script_pubKey
        self.amount = amount

    def serialize(self):
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result

    def lookup_script_pubkey(self, rpc, testnet=False):
        tx = rpc.lookup_transaction(self.prev_tx.hex())
        return tx.tx_outs[self.prev_index].script_pubkey

    def lookup_value(self, rpc, testnet=False):
        # Get the outpoint value by looking up the tx hash Returns the amount in satoshi
        tx = rpc.lookup_transaction(self.prev_tx.hex())     # use self.fetch_tx to get the transaction
        return tx.tx_outs[self.prev_index].amount  #return the amount at the tx out

    @classmethod
    def parse(cls, stream):
        prev_tx_id = stream.read(32)[::-1]
        prev_tx_index = little_endian_to_int(stream.read(4))
        script_sig = Script.parse(stream)
        sequence = little_endian_to_int(stream.read(4))
        return cls(prev_tx_id, prev_tx_index, script_sig, sequence)


class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    def serialize(self):
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result

    @classmethod
    def parse(cls, stream):
        amount = little_endian_to_int(stream.read(8))
        script_pubkey = Script.parse(stream)
        return cls(amount, script_pubkey)
