"""Additive API of the petrelic library.
"""

import msgpack
import petlib.pack as pack

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other

from petrelic.pairing import G2
from petrelic.pairing import G2Element
from petrelic.pairing import NoAffineCoordinateForECPoint

import petrelic.pairing as basepairing


class BilinearGroupPair:
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group Gt.
    """

    def __init__(self):
        """Initialise a bilinear group pair."""
        self.GT = Gt()
        self.G1 = G1()
        self.G2 = G2()

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, Gt.
        """
        return self.G1, self.G2, self.GT


class G1(basepairing.G1):
    """G1 group."""

    @classmethod
    def _element_type(cls):
        return G1Element

    @classmethod
    def prod(cls, elems):
        """Efficient product of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ G1.generator() ** x for x in [10, 25, 13]]
            >>> G1.prod(elems) ==  G1.generator() ** (10 + 25 + 13)
            True
        """
        res = cls.neutral_element()
        for el in elems:
            res *= el
        return res

    @classmethod
    def wprod(cls, weights, elems):
        """Efficient weighted product of a number of elements

        In the current implementation this function is not optimized.
        Example:
            >>> weights = [1, 2, 3]
            >>> elems = [ G1.generator() ** x for x in [10, 25, 13]]
            >>> G1.wprod(weights, elems) ==  G1.generator() ** (1 * 10 + 2 * 25 + 3 * 13)
            True
        """
        res = cls.neutral_element()
        for w, el in zip(weights, elems):
            res *= el ** w

        return res

    unity = basepairing.G1.neutral_element


class G1Element(basepairing.G1Element):
    """Element of the G1 group."""

    group = G1

    def pair(self, other):
        res = GtElement()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res

    square = basepairing.G1Element.double
    isquare = basepairing.G1Element.idouble

    __mul__ = basepairing.G1Element.__add__
    __imul__ = basepairing.G1Element.__iadd__

    __truediv__ = basepairing.G1Element.__sub__
    __itruediv__ = basepairing.G1Element.__isub__

    __pow__ = basepairing.G1Element.__mul__
    __ipow__ = basepairing.G1Element.__imul__

    mul = __mul__
    imul = __imul__
    truediv = __truediv__
    itruediv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__


class G2(basepairing.G2):
    @classmethod
    def _element_type(cls):
        return G2Element

    unity = basepairing.G2.neutral_element


class G2Element(basepairing.G2Element):
    """Element of the G2 group."""

    group = G2

    square = basepairing.G2Element.double
    isquare = basepairing.G2Element.idouble

    __mul__ = basepairing.G2Element.__add__
    __imul__ = basepairing.G2Element.__iadd__

    __truediv__ = basepairing.G2Element.__sub__
    __itruediv__ = basepairing.G2Element.__isub__

    __pow__ = basepairing.G2Element.__mul__
    __ipow__ = basepairing.G2Element.__imul__

    mul = __mul__
    imul = __imul__
    truediv = __truediv__
    itruediv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__



class Gt(basepairing.Gt):
    """Gt group."""

    @classmethod
    def _element_type(cls):
        return GtElement


class GtElement(basepairing.GtElement):
    """Gt element."""

    group = Gt


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
# pack.register_coders(G1Element, 118, pt_enc, pt_dec(G1Element))
# pack.register_coders(G2Element, 119, pt_enc, pt_dec(G2Element))
# pack.register_coders(GtElement, 120, pt_enc, pt_dec(GtElement))
