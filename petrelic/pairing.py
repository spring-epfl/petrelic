from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other
import petrelic.constants as consts

"""Clean API for the petrelic library.
"""

#
# Exceptions
#

class NoAffineCoordinateForECPoint(Exception):
    msg = 'No affine coordinates exists for the given EC point.'


#
# Group pairs
#

class BilinearGroupPair:
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group GT.
    """

    def __init__(self):
        self.gt = Gt()
        self.g1 = G1()
        self.g2 = G2()

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, GT.
        """
        return self.g1, self.g2, self.gt


#
# Group and Elements
#

class G1:
    """G1 group."""

    @staticmethod
    def get_order():
        order = Bn()
        _C.g1_get_ord(order.bn)
        return order

    @staticmethod
    def get_generator():
        generator = G1Element()
        _C.g1_get_gen(generator.pt)
        generator._is_gen = True
        return generator

    @staticmethod
    def get_neutral_element():
        neutral = G1Element()
        _C.g1_set_infty(neutral.pt)
        return neutral


class G1Element():
    """G1 element."""

    def __init__(self):
        self.pt = _FFI.new("g1_t")
        self._is_gen = False
        _C.g1_null(self.pt)
        _C.g1_new(self.pt)

    def __copy__(self):
        copy = G1Element()
        _C.g1_copy(copy.pt, self.pt)
        copy._is_gen = self._is_gen
        return copy

    #
    # Misc
    #

    @staticmethod
    def from_hashed_bytes(hinput):
        res = G1Element()
        _C.g1_map(res.pt, hinput, len(hinput))
        return res

    def is_valid(self):
        return bool(_C.g1_is_valid(self.pt))

    def is_neutral_element(self):
        _C.g1_norm(self.pt, self.pt)
        return bool(_C.g1_is_infty(self.pt))

    def get_double(self):
        res = G1Element()
        _C.g1_dbl(res.pt, self.pt)
        return res

    def double(self):
        self._is_gen = False
        _C.g1_dbl(self.pt, self.pt)
        return self

    def get_affine_coordinates(self):
        if self.is_neutral_element():
            raise NoAffineCoordinateForECPoint()

        x = Bn()
        y = Bn()
        _C.fp_prime_back(x.bn, self.pt[0].x)
        _C.fp_prime_back(y.bn, self.pt[0].y)

        return x, y

    def __hash__(self):
        return self.to_binary().__hash__()

    def __repr__(self):
        pt_hex = self.to_binary().hex()
        return 'G1Element({})'.format(pt_hex)

    #
    # Serialization
    #

    @staticmethod
    def from_binary(sbin):
        elem = G1Element()
        elem._is_gen = False
        _C.g1_read_bin(elem.pt, sbin, len(sbin))
        return elem

    def to_binary(self, compressed=True):
        flag = 1 if compressed else 0
        length = _C.g1_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.g1_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    #
    # Unary operators
    #

    def __neg__(self):
        res = G1Element()
        _C.g1_neg(res.pt, self.pt)
        return res

    #
    # Comparison operators
    #

    def __eq__(self, other):
        if not isinstance(other, G1Element):
            return False

        return _C.g1_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        if not isinstance(other, G1Element):
            return True

        return _C.g1_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Binary operators
    #

    def __add__(self, other):
        res = G1Element()
        _C.g1_add(res.pt, self.pt, other.pt)
        return res

    def __radd__(self, other):
        res = G1Element()
        _C.g1_add(res.pt, other.pt, self.pt)
        return res

    def __iadd__(self, other):
        self._is_gen = False
        _C.g1_add(self.pt, self.pt, other.pt)
        return self

    def __sub__(self, other):
        res = G1Element()
        _C.g1_sub(res.pt, self.pt, other.pt)
        return res

    def __rsub__(self, other):
        res = G1Element()
        _C.g1_sub(res.pt, other.pt, self.pt)
        return res

    def __isub__(self, other):
        self._is_gen = False
        _C.g1_sub(self.pt, self.pt, other.pt)
        return self

    @force_Bn_other
    def __mul__(self, other):
        res = G1Element()
        if self._is_gen:
            _C.g1_mul_gen(res.pt, other.bn)
        else:
            _C.g1_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __rmul__(self, other):
        res = G1Element()
        if self._is_gen:
            _C.g1_mul_gen(res.pt, other.bn)
        else:
            _C.g1_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __imul__(self, other):
        if self._is_gen:
            _C.g1_mul_gen(self.pt, other.bn)
            self._is_gen = False
        else:
            _C.g1_mul(self.pt, self.pt, other.bn)
        return self

    #
    # Aliases
    #

    neg = __neg__
    eq = __eq__
    ne = __ne__
    add = __add__
    radd = __radd__
    iadd = __iadd__
    sub = __sub__
    rsub = __rsub__
    isub = __isub__
    mul = __mul__
    rmul = __rmul__
    imul = __imul__


class G2:
    """G2 group."""

    @staticmethod
    def get_order():
        order = Bn()
        _C.g2_get_ord(order.bn)
        return order

    @staticmethod
    def get_generator():
        generator = G2Element()
        _C.g2_get_gen(generator.pt)
        return generator

    @staticmethod
    def get_neutral_element():
        neutral = G2Element()
        _C.g2_set_infty(neutral.pt)
        return neutral


class G2Element():
    """G2 element."""

    def __init__(self):
        self.pt = _FFI.new("g2_t")
        _C.g2_null(self.pt)
        _C.g2_new(self.pt)

    def __copy__(self):
        copy = G2Element()
        _C.g2_copy(copy.pt, self.pt)
        return copy

    #
    # Misc
    #

    @staticmethod
    def from_hashed_bytes(hinput):
        res = G2Element()
        _C.g2_map(res.pt, hinput, len(hinput))
        return res

    def is_valid(self):
        return bool(_C.g2_is_valid(self.pt))

    def is_neutral_element(self):
        _C.g2_norm(self.pt, self.pt)
        return bool(_C.g2_is_infty(self.pt))

    def get_double(self):
        res = G2Element()
        _C.g2_dbl(res.pt, self.pt)
        return res

    def double(self):
        _C.g2_dbl(self.pt, self.pt)
        return self

    def __hash__(self):
        return self.to_binary().__hash__()

    def __repr__(self):
        pt_hex = self.to_binary().hex()
        return 'G2Element({})'.format(pt_hex)

    #
    # Serialization
    #

    @staticmethod
    def from_binary(sbin):
        elem = G2Element()
        _C.g2_read_bin(elem.pt, sbin, len(sbin))
        return elem

    def to_binary(self, compressed=True):
        flag = int(compressed)
        length = _C.g2_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.g2_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    #
    # Unary operators
    #

    def __neg__(self):
        res = G2Element()
        _C.g2_neg(res.pt, self.pt)
        return res

    #
    # Comparison operators
    #

    def __eq__(self, other):
        if not isinstance(other, G2Element):
            return False

        return _C.g2_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        if not isinstance(other, G2Element):
            return true

        return _C.g2_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Binary operators
    #

    def __add__(self, other):
        res = G2Element()
        _C.g2_add(res.pt, self.pt, other.pt)
        return res

    def __radd__(self, other):
        res = G2Element()
        _C.g2_add(res.pt, other.pt, self.pt)
        return res

    def __iadd__(self, other):
        _C.g2_add(self.pt, self.pt, other.pt)
        return self

    def __sub__(self, other):
        res = G2Element()
        _C.g2_sub(res.pt, self.pt, other.pt)
        return res

    def __rsub__(self, other):
        res = G2Element()
        _C.g2_sub(res.pt, other.pt, self.pt)
        return res

    def __isub__(self, other):
        _C.g2_sub(self.pt, self.pt, other.pt)
        return self

    @force_Bn_other
    def __mul__(self, other):
        res = G2Element()
        _C.g2_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __rmul__(self, other):
        res = G2Element()
        _C.g2_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __imul__(self, other):
        _C.g2_mul(self.pt, self.pt, other.bn)
        return self

    #
    # Aliases
    #

    neg = __neg__
    eq = __eq__
    ne = __ne__
    add = __add__
    radd = __radd__
    iadd = __iadd__
    sub = __sub__
    rsub = __rsub__
    isub = __isub__
    mul = __mul__
    rmul = __rmul__
    imul = __imul__


class Gt:
    """Gt group."""

    @staticmethod
    def get_order():
        order = Bn()
        _C.gt_get_ord(order.bn)
        return order

    @staticmethod
    def get_generator():
        generator = GtElement()
        _C.gt_get_gen(generator.pt)
        return generator

    @staticmethod
    def get_neutral_element():
        neutral = GtElement()
        _C.gt_set_unity(neutral.pt)
        return neutral


class GtElement():
    """Gt element."""

    def __init__(self):
        self.pt = _FFI.new("gt_t")
        _C.gt_null(self.pt)
        _C.gt_new(self.pt)

    def __copy__(self):
        copy = GtElement()
        _C.gt_copy(copy.pt, self.pt)
        return copy
        
    #
    # Misc
    #

    def is_valid(self):
        # TODO: gt_is_valid does not accept unity.
        if bool(_C.gt_is_unity(self.pt)):
            return True

        return bool(_C.gt_is_valid(self.pt))

    def is_neutral_element(self):
        return bool(_C.gt_is_unity(self.pt))

    def get_inverse(self):
        res = GtElement()
        _C.gt_inv(res.pt, self.pt)
        return res

    def inverse(self):
        _C.gt_inv(self.pt, self.pt)
        return self

    def get_square(self):
        res = GtElement()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def square(self):
        _C.gt_sqr(self.pt, self.pt)
        return self

    def __hash__(self):
        return self.to_binary().__hash__()

    def __repr__(self):
        pt_hex = self.to_binary().hex()
        return 'GtElement({})'.format(pt_hex)

    #
    # Serialization
    #

    @staticmethod
    def from_binary(sbin):
        ret = GtElement()
        _C.gt_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def to_binary(self, compressed=True):
        flag = int(compressed)
        length = _C.gt_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.gt_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    #
    # Comparison operators
    #

    def __eq__(self, other):
        if not isinstance(other, GtElement):
            return False

        return _C.gt_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        if not isinstance(other, GtElement):
            return True

        return _C.gt_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Binary operators
    #

    def __mul__(self, other):
        res = GtElement()
        _C.gt_mul(res.pt, self.pt, other.pt)
        return res

    def __rmul__(self, other):
        res = GtElement()
        _C.gt_mul(res.pt, other.pt, self.pt)
        return res

    def __imul__(self, other):
        _C.gt_mul(self.pt, self.pt, other.pt)
        return self

    def __truediv__(self, other):
        res = other.inverse()
        _C.gt_mul(res.pt, self.pt, res.pt)
        return res

    def __itruediv__(self, other):
        other_inv = other.inverse()
        _C.gt_mul(self.pt, self.pt, res.pt)
        return self

    @force_Bn_other
    def __pow__(self, other):
        res = GtElement()
        exponent = other.mod(Gt.get_order())
        _C.gt_exp(res.pt, self.pt, exponent.bn)
        return res

    @force_Bn_other
    def __ipow__(self, other):
        exponent = other.mod(Gt.get_order())
        _C.gt_exp(self.pt, self.pt, exponent.bn)
        return self

    #
    # Aliases
    #

    eq = __eq__
    ne = __ne__
    mul = __mul__
    rmul = __rmul__
    imul = __imul__
    truediv = __truediv__
    itruediv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__
