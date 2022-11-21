from random import randint
from shared.S256Point import B, G, N
from shared.Signature import Signature
from shared.Utility import encode_base58_checksum

import hashlib
import hmac

class PrivateKey:
    def __init__(self, secret):
        self.secret = secret
        self.public_key = secret * G

    def hex(self):
        return '{:x}'.format(self.secret).zfill(64)

    def sign(self, msg_hash):
        k = self.deterministic_k(msg_hash)
        k_inv = pow(k, N-2, N)
        r =(k*G).x.num
        s = (msg_hash + r*self.secret) * k_inv % N
        if s > N/2:
            s = N - s
        return Signature(r,s)

    def deterministic_k(self, z):
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')
        s256 = hashlib.sha256
        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v = hmac.new(k, v, s256).digest()
            candidate = int.from_bytes(v, 'big')
            if candidate >= 1 and candidate < N:
                return candidate  # <2>
            k = hmac.new(k, v + b'\x00', s256).digest()
            v = hmac.new(k, v, s256).digest()

    def wif(self, compressed=True, testnet=False):
        secret_bytes = self.secret.to_bytes(32, 'big')
        if testnet:
            prefix = b'\xef'
        else:
            prefix = b'\x80'
        if compressed:
            suffix = b'\x01'
        else:
            suffix = b''
        return encode_base58_checksum(prefix + secret_bytes + suffix)
