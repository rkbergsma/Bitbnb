from shared.Point import Point
from shared.S256Field import S256Field, P
from shared.Utility import encode_base58_checksum, hash160

N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
A = 0
B = 7

class S256Point(Point):
    def __init__(self, x, y, a=None, b=None):
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=S256Field(A), b=S256Field(B))
        else:
            super().__init__(x=x, y=y, a=S256Field(A), b=S256Field(B))

    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)

    def __repr__(self):
        if(self.x == None):
            return 'S256Point(infinity)'
        return 'S256Point({},{})'.format(hex(self.x.num), hex(self.y.num))

    def verify(self, z, sig):
        s_inv = pow(sig.s, N-2, N)
        u = z * s_inv % N
        v = sig.r * s_inv % N
        total = u*G + v*self
        return total.x.num == sig.r

    def sec(self, compressed=True):
        x_payload = self.x.num.to_bytes(32, 'big')
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + x_payload
            else:
                return b'\x03' + x_payload
        return b'\x04' + x_payload + self.y.num.to_bytes(32, 'big')

    @classmethod
    def parse(cls, sec_bin):
        if sec_bin[0] == 4:
            x = int.from_bytes(sec_bin[1:33], 'big')
            y = int.from_bytes(sec_bin[33:65], 'big')
            return S256Point(x=x, y=y)
        is_even = sec_bin[0] == 2
        x = S256Field(int.from_bytes(sec_bin[1:], 'big'))
        alpha = x**3 + S256Field(B)
        beta = alpha.sqrt()
        if beta.num % 2 == 0:
            even_beta = beta
            odd_beta = S256Field(P - beta.num)
        else:
            even_beta = S256Field(P - beta.num)
            odd_beta = beta
        if is_even:
            return S256Point(x, even_beta)
        else:
            return S256Point(x, odd_beta)

    def hash160(self, compressed=True):
        return hash160(self.sec(compressed))

    def address(self, compressed=True, testnet=False):
        h160 = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'
        return encode_base58_checksum(prefix + h160)

G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    )