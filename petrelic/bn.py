from petrelic.bindings import _FFI, _C
import petrelic.constants as consts

import functools
import re


def force_Bn(n):
    """A decorator that coerces the nth input to be a Big Number"""

    def decorator_force_Bn(func):
        # pylint: disable=star-args
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_args = args
            if n < len(args) and not isinstance(args[n], Bn):
                if isinstance(args[n], int):
                    new_args = list(args)
                    new_args[n] = Bn(new_args[n])
                    new_args = tuple(new_args)
                else:
                    # Don't know how to convert
                    return NotImplemented

            return func(*new_args, **kwargs)

        return wrapper

    return decorator_force_Bn


def force_Bn_other(func):
    return force_Bn(1)(func)


class Bn(object):

    __slots__ = ["bn"]

    @staticmethod
    def from_num(num):
        if isinstance(num, int):
            return Bn(num)
        elif isinstance(num, Bn):
            return num
        else:
            # raise TypeError("Cannot coerce %s into a BN." % num)
            return NotImplemented

    @staticmethod
    def _from_radix_string(sinput, radix):
        neg = False
        if sinput[0] == "-":
            neg = True
            sinput = sinput[1:]

        ret = Bn()
        s = sinput.encode("utf8")
        _C.bn_read_str(ret.bn, s, len(s), radix)

        if neg:
            return ret.__neg__()
        else:
            return ret

    @staticmethod
    def from_decimal(sdec):
        """Creates a Big Number from a decimal string.

        Args:
            sdec (string): numeric string possibly starting with minus.

        See Also:
            str() produces a decimal string from a big number.

        Example:
            >>> hundred = Bn.from_decimal("100")
            >>> str(hundred)
            '100'
        """

        if not re.match("-?[0-9]+$", sdec):
            raise Exception("String must only contain digits 0--9 and sign")

        return Bn._from_radix_string(sdec, 10)

    @staticmethod
    def from_hex(shex):
        """Creates a Big Number from a hexadecimal string.

        Args:
            shex (string): hex (0-F) string possibly starting with minus.

        See Also:
            hex() produces a hexadecimal representation of a big number.

        Example:
            >>> Bn.from_hex("FF")
            Bn(255)
        """

        if not re.match("-?[0-9a-fA-F]+$", shex):
            raise Exception("String must only contain digits 0--9,a--f and sign")

        shex = shex.lower()
        return Bn._from_radix_string(shex, 16)

    @staticmethod
    def from_binary(sbin):
        """ Restore number given its Big-endian representation.

        Creates a Big Number from a byte sequence representing the number in
        Big-endian 8 byte atoms. Only positive values can be represented as
        byte sequence, and the library user should store the sign bit
        separately.

        Args:
            sbin (string): a byte sequence.

        Example:
            >>> from binascii import unhexlify
            >>> byte_seq = unhexlify(b"010203")
            >>> Bn.from_binary(byte_seq)
            Bn(66051)
            >>> (1 * 256**2) + (2 * 256) + 3
            66051
        """
        ret = Bn()
        _C.bn_read_bin(ret.bn, sbin, len(sbin))
        return ret

    @staticmethod
    def get_prime(bits, safe=1):
        """
        Builds a prime Big Number of length bits.

        Args:
                bits (int) -- the number of bits.
                safe (int) -- 1 for a safe prime, otherwise 0.
        """

        ret = Bn()
        if safe == 1:
            _C.bn_gen_prime_safep(ret.bn, bits)
        else:
            _C.bn_gen_prime(ret.bn, bits)

        return ret

    @staticmethod
    def get_random(bits):
        """
        Generates a random number of the given number of bits

        Args:
            bits (int) -- The number of bits

        Examples:

            >>> n = Bn.get_random(10)
            >>> n.num_bits() <= 10
            True
        """
        res = Bn()
        _C.bn_rand(res.bn, 0, bits)
        return res

    def __init__(self, num=0):
        """Initialize a new Bn, initialized with a small integer"""
        self.bn = _FFI.new("bn_t")
        _C.bn_new(self.bn)

        if abs(num) < consts.DIGIT_MAXIMUM:
            _C.bn_set_dig(self.bn, abs(num))
        else:
            length = num.bit_length() // 8 + 1
            sbin = abs(num).to_bytes(length, byteorder='big', signed=False)
            _C.bn_read_bin(self.bn, sbin, len(sbin))

        if num < 0:
            _C.bn_neg(self.bn, self.bn)

    def copy(self):
        """Returns a copy of the Bn object."""
        return self.__copy__()

    def __copy__(self):
        # 'Copies the big number. Support for copy module'
        other = Bn()
        _C.bn_copy(other.bn, self.bn)
        return other

    def __deepcopy__(self, memento):
        # 'Deepcopy is the same as copy'
        # pylint: disable=unused-argument
        return self.__copy__()

    # ------------ Comparisons ------------

    @force_Bn_other
    def __inner_cmp__(self, other):
        sig = int(_C.bn_cmp(self.bn, other.bn))
        return sig

    def __lt__(self, other):
        return self.__inner_cmp__(other) < 0

    def __le__(self, other):
        return self.__inner_cmp__(other) <= 0

    def __eq__(self, other):
        return self.__inner_cmp__(other) == 0

    def __ne__(self, other):
        return self.__inner_cmp__(other) != 0

    def __gt__(self, other):
        return self.__inner_cmp__(other) > 0

    def __ge__(self, other):
        return self.__inner_cmp__(other) >= 0

    def bool(self):
        """Turn Bn into boolean. False if zero, True otherwise.

        Examples:
            >>> bool(Bn(0))
            False
            >>> bool(Bn(1337))
            True

        """
        return self.__bool__()

    def __bool__(self):
        # 'Turn into boolean'
        return not bool(_C.bn_is_zero(self.bn))

    def repr(self):
        return self.__repr__()

    def __repr__(self):
        # TODO: return value may be too big, in which case it cannot be recovered
        return "Bn({})".format(self.repr_in_base(10))

    def __str__(self):
        return self.repr_in_base(10)

    def int(self):
        """A native python integer representation of the Big Number.
             Synonym for int(bn).
        """
        return self.__int__()

    def __int__(self):
        return int(self.repr_in_base(10))

    def __index__(self):
        return self.__int__()

    def hex(self):
        """The representation of the string in hexadecimal.
        Synonym for hex(n)."""
        return self.__hex__()

    def __hex__(self):
        # """The representation of the string in hexadecimal"""
        return self.repr_in_base(16)

    # NOT_IMPLEMENTED: hex()

    def binary(self):
        """A byte array representing the absolute value

        A byte array representation of the absolute value in Big-Endian format
        (with 8 bit atomic elements). You are responsible for extracting the
        sign bit separately.

        Example:
            >>> from binascii import hexlify

            >>> bin = Bn(66051).binary()
            >>> hexlify(bin) == b'010203'
            True

            >>> bin = Bn(1337).binary()
            >>> hexlify(bin) == b'0539'
            True

        """
        if self < 0:
            raise Exception("Cannot represent negative numbers")

        length = _C.bn_size_bin(self.bn)
        buf = _FFI.new("char[]", length)
        _C.bn_write_bin(buf, length, self.bn)
        return _FFI.unpack(buf, length)

    def repr_in_base(self, radix):
        """ Represent number as string in given base

        Args:
            radix (int): The number of unique digits (2 <= radix <= 62)

        Examples:
            >>> Bn(42).repr_in_base(16)
            '2A'
            >>> Bn(-1024).repr_in_base(2)
            '-10000000000'
        """
        length = _C.bn_size_str(self.bn, radix)
        buf = _FFI.new("char[]", length)
        _C.bn_write_str(buf, length, self.bn, radix)
        return _FFI.string(buf).decode("utf8")

    def test(self):
        """
        >>> b = Bn()
        >>> b.repr_in_base(2)
        '0'
        """

    def random(self):
        """Returns a random number 0 < rand < self

        TODO: currently it excludes 0, update to include 0

        Example:
            #>>> r = Bn(100).random()
            #>>> 0 <= r && r < 100
            True
        """
        rnd = Bn()
        _C.bn_rand_mod(rnd.bn, self.bn)
        return rnd

    # ---------- Arithmetic --------------
    def int_neg(self):
        """Returns the negative of this number. Synonym with -self.

        Example:

            >>> one100 = Bn(100)
            >>> one100.int_neg()
            Bn(-100)
            >>> -one100
            Bn(-100)
        """
        return self.__neg__()

    def int_add(self, other):
        """Returns the sum of this number with another. Synonym for self + other.

        Example:
            >>> one100 = Bn(100)
            >>> two100 = Bn(200)
            >>> two100.int_add(one100) # Function syntax
            Bn(300)
            >>> two100 + one100        # Operator syntax
            Bn(300)
        """
        return self.__add__(other)

    def __radd__(self, other):
        return self.__add__(other)

    @force_Bn_other
    def __add__(self, other):
        r = Bn()
        _C.bn_add(r.bn, self.bn, other.bn)
        return r

    def int_sub(self, other):
        """Returns the difference between this number and another.
        Synonym for self - other.

        Example:
            >>> one100 = Bn(100)
            >>> two100 = Bn(200)
            >>> two100.int_sub(one100) # Function syntax
            Bn(100)
            >>> two100 - one100        # Operator syntax
            Bn(100)
        """
        return self.__sub__(other)

    @force_Bn_other
    def __rsub__(self, other):
        return other - self

    @force_Bn_other
    def __sub__(self, other):
        r = Bn()
        _C.bn_sub(r.bn, self.bn, other.bn)
        return r

    def int_mul(self, other):
        """Returns the product of this number with another.
        Synonym for self * other.

        Example:
            >>> one100 = Bn(100)
            >>> two100 = Bn(200)
            >>> one100.int_mul(two100) # Function syntax
            Bn(20000)
            >>> one100 * two100        # Operator syntax
            Bn(20000)
        """
        return self.__mul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    @force_Bn_other
    def __mul__(self, other):
        r = Bn()
        _C.bn_mul(r.bn, self.bn, other.bn)
        return r

    def __neg__(self):
        ret = Bn()
        _C.bn_neg(ret.bn, self.bn)
        return ret

    def __abs__(self):
        ret = Bn()
        _C.bn_abs(ret.bn, self.bn)
        return ret

    # ------------------ Mod arithmetic -------------------------

    @force_Bn(1)
    @force_Bn(2)
    def mod_add(self, other, m):
        """ Returns the sum of self and other modulo m.

        Example:
            >>> Bn(10).mod_add(2, 11)
            Bn(1)
            >>> Bn(10).mod_add(Bn(2), Bn(11))
            Bn(1)
        """

        r = Bn()
        _C.bn_add(r.bn, self.bn, other.bn)
        _C.bn_mod(r.bn, r.bn, m.bn)
        return r

    @force_Bn(1)
    @force_Bn(2)
    def mod_sub(self, other, m):
        """ Returns the difference of self and other modulo m.

        Example:
            >>> Bn(10).mod_sub(Bn(2), Bn(11))
            Bn(8)
        """

        r = Bn()
        _C.bn_sub(r.bn, self.bn, other.bn)
        _C.bn_mod(r.bn, r.bn, m.bn)
        return r

    @force_Bn(1)
    @force_Bn(2)
    def mod_mul(self, other, m):
        """ Return the product of self and other modulo m.

        Example:
            >>> Bn(10).mod_mul(Bn(2), Bn(11))
            Bn(9)
        """

        r = Bn()
        _C.bn_mul(r.bn, self.bn, other.bn)
        _C.bn_mod(r.bn, r.bn, m.bn)
        return r

    @force_Bn_other
    def mod_inverse(self, m):
        """ Compute the inverse mod m, such that self * res == 1 mod m.

        Example:
            >>> Bn(10).mod_inverse(m = Bn(11))
            Bn(10)
            >>> Bn(10).mod_mul(Bn(10), m = Bn(11)) == Bn(1)
            True
        """
        gcd = Bn()
        inv = Bn()
        _C.bn_gcd_ext(gcd.bn, inv.bn, _FFI.NULL, self.bn, m.bn)
        _C.bn_mod(inv.bn, inv.bn, m.bn)

        if gcd != Bn(1):
            raise Exception("No inverse for ", self, "modulo ", m)

        return inv

    def mod_pow(self, other, m, ctx=None):
        """ Performs the modular exponentiation of self ** other % m.

            This function is _not_ constant time.

            Example:
                >>> one100 = Bn(100)
                >>> one100.mod_pow(2, 3)   # Modular exponentiation
                Bn(1)
        """
        return self.__pow__(other, m)

    def divmod(self, other):
        """Returns the integer division and remainder of this number by another.

        Example:
            >>> Bn(13).divmod(Bn(9))
            (Bn(1), Bn(4))
        """
        return self.__divmod__(other)

    def __rdivmod__(self, other):
        return Bn(other).__divmod__(self)

    @force_Bn_other
    def __divmod__(self, other):
        quot = Bn()
        rem = Bn()
        _C.bn_div_rem(quot.bn, rem.bn, self.bn, other.bn)
        return (quot, rem)

    def int_div(self, other):
        """Returns the integer division of this number by another.
        Synonym of self / other.

        Example:
            >>> one100 = Bn(100)
            >>> two100 = Bn(200)
            >>> two100.int_div(one100) # Function syntax
            Bn(2)
            >>> two100 // one100        # Operator syntax
            Bn(2)
        """
        return self.__floordiv__(other)

    @force_Bn_other
    def __rfloordiv__(self, other):
        return other.__floordiv__(self)

    @force_Bn_other
    def __floordiv__(self, other):
        quot = Bn()
        _C.bn_div(quot.bn, self.bn, other.bn)
        return quot

    def mod(self, other):
        """Returns the remainder of this number modulo another.
        Synonym for self % other.

        Example:
            >>> one100 = Bn(100)
            >>> two100 = Bn(200)
            >>> two100.mod(one100) # Function syntax
            Bn(0)
            >>> two100 % one100        # Operator syntax
            Bn(0)
        """
        return self.__mod__(other)

    @force_Bn_other
    def __rmod__(self, other):
        return other.__mod__(self)

    @force_Bn_other
    def __mod__(self, other):
        rem = Bn()
        _C.bn_mod(rem.bn, self.bn, other.bn)
        return rem

    def pow(self, other, modulo=None):
        """Returns the number raised to the power other optionally modulo a third number.
        Synonym with pow(self, other, modulo).

        Example:
            >>> one100 = Bn(100)
            >>> one100.pow(2)      # Function syntax
            Bn(10000)
            >>> one100 ** 2        # Operator syntax
            Bn(10000)
            >>> one100.pow(2, 3)   # Modular exponentiation
            Bn(1)
        """
        return self.__pow__(other, modulo)

    @force_Bn_other
    def __rpow__(self, other):
        return other.__pow__(self)

    @force_Bn_other
    def __pow__(self, n, modulo=None):
        if n < 0 and modulo is None:
            raise ArithmeticError(
                "Negative exponent only supported when modulus is set"
            )

        # TODO: fix coercions later
        if type(modulo) == int:
            modulo = Bn(modulo)

        base = Bn()
        _C.bn_copy(base.bn, self.bn)

        if _C.bn_sign(n.bn) == _C.CONST_RLC_NEG:
            base = base.mod_inverse(modulo)
            _C.bn_neg(n.bn)

        if _C.bn_is_zero(n.bn) == 1:
            return Bn(1)

        res = Bn(1)
        if modulo is None:
            while not bool(_C.bn_is_zero(n.bn)):
                if n.is_odd():
                    res = res * base

                _C.bn_sqr(base.bn, base.bn)
                _C.bn_hlv(n.bn, n.bn)
            return res
        else:
            # TODO: rewrite using bn_mxp
            while not bool(_C.bn_is_zero(n.bn)):
                if n.is_odd():
                    res = res.mod_mul(base, modulo)

                base = base.mod_mul(base, modulo)
                _C.bn_hlv(n.bn, n.bn)
            return res

    def is_prime(self):
        """Returns True if the number is prime, with negligible prob. of error.

        Examples:
            >>> Bn(37).is_prime()
            True
            >>> Bn(10).is_prime()
            False
        """
        return _C.bn_is_prime(self.bn) == 1

    def is_odd(self):
        """Returns True if the number is odd.

        Examples:
            >>> Bn(2).is_odd()
            False
            >>> Bn(1337).is_odd()
            True
        """

        return not bool(_C.bn_is_even(self.bn))

    def is_even(self):
        """Returns True if the number is even.

        Examples:
            >>> Bn(2).is_even()
            True
            >>> Bn(1337).is_even()
            False
        """

        return bool(_C.bn_is_even(self.bn))

    def is_bit_set(self, n):
        """Returns True if the nth bit is set

        Examples:
            >>> a = Bn(17) # in binary 10001
            >>> a.is_bit_set(0)
            True
            >>> a.is_bit_set(1)
            False
            >>> a.is_bit_set(4)
            True
        """
        bit = _C.bn_get_bit(self.bn, n)
        return bool(bit)

    def num_bits(self):
        """Returns the number of bits representing this Big Number"""
        return int(_C.bn_bits(self.bn))

    def __hash__(self):
        return int(self).__hash__()

    # Aliases
    abs = __abs__
