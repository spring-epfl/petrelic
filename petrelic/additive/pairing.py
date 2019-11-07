"""Additive API of the petrelic library.
"""

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other

from petrelic.pairing import (
    G1,
    G2,
    G1Element,
    G2Element,
    NoAffineCoordinateForECPoint
)

class BilinearGroupPair:
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group Gt.
    """

    def __init__(self):
        self.GT = Gt()
        self.G1 = G1()
        self.G2 = G2()

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, Gt.
        """
        return self.G1, self.G2, self.GT


class Gt:
    """Gt group."""

    @staticmethod
    def get_order():
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = Gt.get_generator()
            >>> neutral = Gt.get_neutral_element()
            >>> order = Gt.get_order()
            >>> generator * order == neutral
            True
        """
        order = Bn()
        _C.gt_get_ord(order.bn)
        return order

    @staticmethod
    def get_generator():
        """Return generator of the EC group.

        Example:
            >>> generator = Gt.get_generator()
            >>> neutral = Gt.get_neutral_element()
            >>> generator + neutral == generator
            True
        """
        generator = GtElement()
        _C.gt_get_gen(generator.pt)
        return generator

    @staticmethod
    def get_neutral_element():
        """Return the neutral element of the group Gt.
        In this case, the unity point.

        Example:
            >>> generator = Gt.get_generator()
            >>> neutral = Gt.get_neutral_element()
            >>> generator + neutral == generator
            True
        """
        neutral = GtElement()
        _C.gt_set_unity(neutral.pt)
        return neutral

    #
    # Aliases
    #


class GtElement():
    """Gt element."""

    def __init__(self):
        """Initialize a new element of Gt."""
        self.pt = _FFI.new("gt_t")
        _C.gt_null(self.pt)
        _C.gt_new(self.pt)

    def __copy__(self):
        """Clone an element of Gt."""
        copy = GtElement()
        _C.gt_copy(copy.pt, self.pt)
        return copy

    #
    # Misc
    #

    def is_valid(self):
        """Check if the data of this object is indeed a point on the EC.

        Example:
            >>> elem = Gt.get_generator()
            >>> elem.is_valid()
            True
        """
        # TODO: gt_is_valid does not accept unity.
        if bool(_C.gt_is_unity(self.pt)):
            return True

        return bool(_C.gt_is_valid(self.pt))

    def is_neutral_element(self):
        """Check if the object is the neutral element of Gt.

        Example:
            >>> generator = Gt.get_generator()
            >>> order = Gt.get_order()
            >>> elem = generator * order
            >>> elem.is_neutral_element()
            True
        """
        return bool(_C.gt_is_unity(self.pt))

    def iinverse(self):
        """Inverse the element of Gt."""
        _C.gt_inv(self.pt, self.pt)
        return self

    def double(self):
        """Return an element which is the double of the current one.

        Example:
            >>> generator = Gt.get_generator()
            >>> elem = generator.double()
            >>> elem == generator * 2
            True
        """
        res = GtElement()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def idouble(self):
        """Double the current element.

        Example:
            >>> generator = Gt.get_generator()
            >>> elem = Gt.get_generator().idouble()
            >>> elem == generator * 2
            True
        """
        _C.gt_sqr(self.pt, self.pt)
        return self

    def __hash__(self):
        """Hash function used internally by Python."""
        return self.to_binary().__hash__()

    def __repr__(self):
        """String representation of the element of G2."""
        pt_hex = self.to_binary().hex()
        return 'GtElement({})'.format(pt_hex)

    #
    # Serialization
    #

    @staticmethod
    def from_binary(sbin):
        """Deserialize a binary representation of the element of Gt.

        Example:
            >>> generator = Gt.get_generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = GtElement.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        ret = GtElement()
        _C.gt_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def to_binary(self, compressed=True):
        """Serialize the element of Gt into a binary representation.

        Example:
            >>> generator = Gt.get_generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = GtElement.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        flag = int(compressed)
        length = _C.gt_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.gt_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    #
    # Unary operators
    #

    def __neg__(self):
        """Return the inverse of the element of Gt."""
        res = GtElement()
        _C.gt_inv(res.pt, self.pt)
        return res

    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points on the EC are equal."""
        if not isinstance(other, GtElement):
            return False

        return _C.gt_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
        if not isinstance(other, GtElement):
            return True

        return _C.gt_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Binary operators
    #

    def __add__(self, other):
        res = GtElement()
        _C.gt_mul(res.pt, self.pt, other.pt)
        return res

    def __radd__(self, other):
        res = GtElement()
        _C.gt_mul(res.pt, other.pt, self.pt)
        return res

    def __iadd__(self, other):
        _C.gt_mul(self.pt, self.pt, other.pt)
        return self

    def __sub__(self, other):
        res = other.inverse()
        _C.gt_mul(res.pt, self.pt, res.pt)
        return res

    def __rsub__(self, other):
        res = self.inverse()
        _C.gt_mul(res.pt, other.pt, res.pt)
        return res

    def __isub__(self, other):
        other_inv = other.inverse()
        _C.gt_mul(self.pt, self.pt, other_inv.pt)
        return self

    @force_Bn_other
    def __mul__(self, other):
        res = GtElement()
        exponent = other.mod(Gt.get_order())
        _C.gt_exp(res.pt, self.pt, exponent.bn)
        return res

    @force_Bn_other
    def __rmul__(self, other):
        res = GtElement()
        exponent = other.mod(Gt.get_order())
        _C.gt_exp(res.pt, self.pt, exponent.bn)
        return res

    @force_Bn_other
    def __imul__(self, other):
        exponent = other.mod(Gt.get_order())
        _C.gt_exp(self.pt, self.pt, exponent.bn)
        return self

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    inverse = __neg__
    neg = __neg__
    eq = __eq__
    ne = __ne__
    add = __add__
    iadd = __iadd__
    sub = __sub__
    isub = __isub__
    mul = __mul__
    imul = __imul__
