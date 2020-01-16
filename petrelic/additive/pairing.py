"""Additive API of the petrelic library.
"""

import msgpack
import petlib.pack as pack

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other

from petrelic.pairing import G2
from petrelic.pairing import G2Element
from petrelic.pairing import NoAffineCoordinateForECPoint

import petrelic.pairing as mulpairing

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


class G1(mulpairing.G1):
    """G1 group."""

    @classmethod
    def element_type(cls):
        return G1Element


class G1Element(mulpairing.G1Element):
    """Element of the G1 group."""

    group = G1

    def pair(self, other):
        res = GtElement()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res


class Gt(mulpairing.Gt):
    """Gt group."""

    @classmethod
    def element_type(cls):
        return GtElement

    get_infinity = mulpairing.Gt.get_neutral_element
    infinite = mulpairing.Gt.get_neutral_element


class GtElement(mulpairing.GtElement):
    """Gt element."""

    group = Gt

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


    #
    # Unary operators
    #

    def __neg__(self):
        """Return the inverse of the element of Gt."""
        res = GtElement()
        _C.gt_inv(res.pt, self.pt)
        return res

    #
    # Binary operators
    #

    double = mulpairing.GtElement.square
    idouble = mulpairing.GtElement.isquare

    __add__ = mulpairing.GtElement.__mul__
    __radd__ = mulpairing.GtElement.__rmul__
    __iadd__ = mulpairing.GtElement.__imul__

    __sub__ = mulpairing.GtElement.__truediv__
    __isub__ = mulpairing.GtElement.__itruediv__

    __mul__ = mulpairing.GtElement.__pow__
    __imul__ = mulpairing.GtElement.__ipow__

    def __rsub__(self, other):
        res = self.inverse()
        _C.gt_mul(res.pt, other.pt, res.pt)
        return res

    @force_Bn_other
    def __rmul__(self, other):
        res = GtElement()
        exponent = other.mod(Gt.get_order())
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
pack.register_coders(G1Element, 114, pt_enc, pt_dec(G1Element))
pack.register_coders(G2Element, 115, pt_enc, pt_dec(G2Element))
pack.register_coders(GtElement, 116, pt_enc, pt_dec(GtElement))
