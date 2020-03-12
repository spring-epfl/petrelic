"""Additive API of the petrelic library.
"""

import msgpack
import petlib.pack as pack

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other
from petrelic.native.pairing import NoAffineCoordinateForECPoint

import petrelic.native.pairing as native
from petrelic.native.pairing import G2, G2Element

class BilinearGroupPair:
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group GT.
    """

    def __init__(self):
        """Initialise a bilinear group pair."""
        self.GT = GT()
        self.G1 = G1()
        self.G2 = G2()

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, GT.
        """
        return self.G1, self.G2, self.GT


class G1(native.G1):
    """G1 group."""

    @classmethod
    def _element_type(cls):
        return G1Element


class G1Element(native.G1Element):
    """Element of the G1 group."""

    group = G1

    def pair(self, other):
        res = GTElement()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res


class GT(native.GT):
    """GT group."""

    @classmethod
    def _element_type(cls):
        return GTElement

    @classmethod
    def sum(cls, elems):
        """Efficient sum of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ x * GT.generator() for x in [10, 25, 13]]
            >>> GT.sum(elems) ==  (10 + 25 + 13) * GT.generator()
            True
        """
        res = cls.neutral_element()
        for el in elems:
            res += el

        return res

    @classmethod
    def wsum(cls, weights, elems):
        """Efficient weighted product of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> weights = [1, 2, 3]
            >>> elems = [ x * GT.generator() for x in [10, 25, 13]]
            >>> GT.wsum(weights, elems) ==  (1 * 10 + 2 * 25 + 3 * 13) * GT.generator()
            True
        """
        res = cls.neutral_element()
        for w, el in zip(weights, elems):
            res += w * el

        return res

    infinity = native.GT.neutral_element


class GTElement(native.GTElement):
    """GT element."""

    group = GT

    def iinverse(self):
        """Inverse the element of GT."""
        _C.gt_inv(self.pt, self.pt)
        return self

    def double(self):
        """Return an element which is the double of the current one.

        Example:
            >>> generator = GT.generator()
            >>> elem = generator.double()
            >>> elem == generator * 2
            True
        """
        res = GTElement()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def idouble(self):
        """Double the current element.

        Example:
            >>> generator = GT.generator()
            >>> elem = GT.generator().idouble()
            >>> elem == generator * 2
            True
        """
        _C.gt_sqr(self.pt, self.pt)
        return self


    #
    # Unary operators
    #

    def __neg__(self):
        """Return the inverse of the element of GT."""
        res = GTElement()
        _C.gt_inv(res.pt, self.pt)
        return res

    #
    # Binary operators
    #

    double = native.GTElement.square
    idouble = native.GTElement.isquare

    __add__ = native.GTElement.__mul__
    __iadd__ = native.GTElement.__imul__

    __sub__ = native.GTElement.__truediv__
    __isub__ = native.GTElement.__itruediv__

    __mul__ = native.GTElement.__pow__
    __imul__ = native.GTElement.__ipow__

    @force_Bn_other
    def __rmul__(self, other):
        res = GTElement()
        exponent = other.mod(GT.order())
        _C.gt_exp(res.pt, self.pt, exponent.bn)
        return res

    #
    # Aliases
    #

    inverse = __neg__
    neg = __neg__
    add = __add__
    iadd = __iadd__
    sub = __sub__
    isub = __isub__
    mul = __mul__
    imul = __imul__


def pt_enc(obj):
    """Encoder for the wrapped points."""
    data = obj.to_binary()
    packed_data = msgpack.packb(data)
    return packed_data


def pt_dec(bptype):
    """Decoder for the wrapped points."""

    def dec(data):
        data_extracted = msgpack.unpackb(data)
        pt = bptype.from_binary(data_extracted)
        return pt

    return dec

# Register encoders and decoders for pairing points
# pack.register_coders(G1Element, 114, pt_enc, pt_dec(G1Element))
# pack.register_coders(G2Element, 115, pt_enc, pt_dec(G2Element))
# pack.register_coders(GTElement, 116, pt_enc, pt_dec(GTElement))
