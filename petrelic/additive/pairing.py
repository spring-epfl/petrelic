r"""
This module provides a Python wrapper around RELIC's pairings using a
additive interface: operations in
:py:obj:`petrelic.additive.pairings.G1`,
:py:obj:`petrelic.additive.pairings.G2`, and 
:py:obj:`petrelic.additive.pairings.GT` are all written
additively.

Let's see how we can use this interface to implement the Boney-Lynn-Shacham
signature scheme for type III pairings. First we generate a private key:

>>> sk = G1.order().random()

which is a random integer modulo the group order. Note that for this setting,
all three groups have the same order. Next, we generate the corresponding public
key:

>>> pk = (sk * G1.generator(), sk * G2.generator())

(For security in the type III setting, the first component is a necessary part
of the public key. It is not actually used in the scheme.) To sign a message
`m` we first hash it to the curve G1 using :py:meth:`G1.hash_to_point` and then
raise it to the power of the signing key `sk` to obtain a signature:

>>> m = b"Some message"
>>> signature = sk * G1.hash_to_point(m)

Finally, we can use the pairing operator to verify the signature:

>>> signature.pair(G2.generator()) == G1.hash_to_point(m).pair(pk[1])
True

Indeed, the pairing operator is bilinear. For example:

>>> a, b = 13, 29
>>> A = a * G1.generator()
>>> B = b * G2.generator()
>>> A.pair(B) == (a*b) * G1.generator().pair(G2.generator())
True

"""

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


class G2(native.G2):
    """G2 group."""

    @classmethod
    def _element_type(cls):
        return G2Element


class G2Element(native.G2Element):
    """Element of the G2 group."""

    group = G2


class GT(native._GTBase):
    """GT group."""

    @classmethod
    def _element_type(cls):
        return GTElement

    #
    # Replicated functions, fixing doc strings
    #

    @classmethod
    def order(cls):
        """Return the order of the group as a Bn large integer.

        Example:
            >>> generator = GT.generator()
            >>> neutral = GT.neutral_element()
            >>> order = GT.order()
            >>> order * generator == neutral
            True
        """
        return super().order()

    @classmethod
    def generator(cls):
        """Return generator of the group.

        Example:
            >>> generator = GT.generator()
            >>> neutral = GT.neutral_element()
            >>> generator + neutral == generator
            True
        """
        return super().generator()

    @classmethod
    def neutral_element(cls):
        """Return the neutral element of the group G1.

        In this case, the point at infinity.

        Example:
            >>> generator = GT.generator()
            >>> neutral = GT.neutral_element()
            >>> generator + neutral == generator
            True
        """
        return super().neutral_element()

    #
    # Interface specific methods
    #

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

    #
    # Aliases
    #


    @classmethod
    def infinity(cls):
        """The unity element

        Alias for :py:meth:`GT.neutral_element`
        """
        return cls.neutral_element()


class GTElement(native._GTElementBase):
    """GT element."""

    group = GT

    #
    # Unary operators
    #


    def double(self):
        return native.GTElement.square(self)

    def idouble(self):
        return native.GTElement.isquare(self)

    #
    # Binary operators
    #

    def __add__(self, other):
        return native.GTElement.__mul__(self, other)

    def __iadd__(self, other):
        return native.GTElement.__imul__(self, other)

    def __sub__(self, other):
        return native.GTElement.__truediv__(self, other)

    def __isub__(self, other):
        return native.GTElement.__itruediv__(self, other)

    def __mul__(self, other):
        return native.GTElement.__pow__(self, other)

    def __imul__(self, other):
        return native.GTElement.__ipow__(self, other)

    def __rmul__(self, other):
        return native.GTElement.__pow__(self, other)

    # Copy documentation from native.G1Element
    double.__doc__ = native.G1Element.double.__doc__.replace("G1", "GT")
    idouble.__doc__ = native.G1Element.idouble.__doc__.replace("G1", "GT")

    __add__.__doc__ = native.G1Element.__add__.__doc__.replace("G1", "GT")
    __iadd__.__doc__ = native.G1Element.__iadd__.__doc__.replace("G1", "GT")

    __sub__.__doc__ = native.G1Element.__sub__.__doc__.replace("G1", "GT")
    __isub__.__doc__ = native.G1Element.__isub__.__doc__.replace("G1", "GT")

    __mul__.__doc__ = native.G1Element.__mul__.__doc__.replace("G1", "GT")
    __imul__.__doc__ = native.G1Element.__imul__.__doc__.replace("G1", "GT")

    #
    # Aliases
    #

    __neg__ = native._GTElementBase.inverse
    neg = __neg__

    add = __add__
    iadd = __iadd__
    sub = __sub__
    isub = __isub__
    mul = __mul__
    imul = __imul__
