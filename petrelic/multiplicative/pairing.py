r"""
This module provides a Python wrapper around RELIC's pairings using a
multiplicative interface: operations in
:py:obj:`petrelic.multiplicative.pairings.G1`,
:py:obj:`petrelic.multiplicative.pairings.G2`, and
:py:obj:`petrelic.multiplicative.pairings.GT` are all written
multiplicatively.

Let's see how we can use this interface to implement the Boney-Lynn-Shacham
signature scheme for type III pairings. First we generate a private key:

>>> sk = G1.order().random()

which is a random integer modulo the group order. Note that for this setting,
all three groups have the same order. Next, we generate the corresponding public
key:

>>> pk = (G1.generator() ** sk, G2.generator() ** sk)

(For security in the type III setting, the first component is a necessary part
of the public key. It is not actually used in the scheme.) To sign a message
`m` we first hash it to the curve G1 using :py:meth:`G1.hash_to_point` and then
raise it to the power of the signing key `sk` to obtain a signature:

>>> m = b"Some message"
>>> signature = G1.hash_to_point(m) ** sk

Finally, we can use the pairing operator to verify the signature:

>>> signature.pair(G2.generator()) == G1.hash_to_point(m).pair(pk[1])
True

Indeed, the pairing operator is bilinear. For example:

>>> a, b = 13, 29
>>> A = G1.generator() ** a
>>> B = G2.generator() ** b
>>> A.pair(B) == G1.generator().pair(G2.generator()) ** (a * b)
True

"""

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other
from petrelic.native.pairing import NoAffineCoordinateForECPoint

import petrelic.native.pairing as native


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


class G1(native._G1Base):
    """G1 group."""

    @classmethod
    def _element_type(cls):
        return G1Element

    #
    # Replicated functions, fixing doc strings
    #

    @classmethod
    def order(cls):
        """Return the order of the group as a Bn large integer.

        Example:
            >>> generator = G1.generator()
            >>> neutral = G1.neutral_element()
            >>> order = G1.order()
            >>> generator ** order == neutral
            True
        """
        return super().order()

    @classmethod
    def generator(cls):
        """Return generator of the group.

        Example:
            >>> generator = G1.generator()
            >>> neutral = G1.neutral_element()
            >>> generator * neutral == generator
            True
        """
        return super().generator()

    @classmethod
    def neutral_element(cls):
        """Return the neutral element of the group G1.

        In this case, the point at infinity.

        Example:
            >>> generator = G1.generator()
            >>> neutral = G1.neutral_element()
            >>> generator * neutral == generator
            True
        """
        return super().neutral_element()

    #
    # Interface specific methods
    #

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

    #
    # Aliases
    #

    @classmethod
    def unity(cls):
        """The unity element

        Alias for :py:meth:`G1.neutral_element`
        """
        return cls.neutral_element()


class G1Element(native._G1ElementBase):
    """Element of the G1 group."""

    group = G1

    def pair(self, other):
        """Pair element with another element in G2

        Computes the bilinear pairing between self and another element in
        :py:obj:`petrelic.multiplicative.pairing.G2`.

        Examples:
             >>> g1, g2 = G1.generator(), G2.generator()
             >>> a, b = 10, 50
             >>> A, B = g1 ** a, g2 ** b
             >>> A.pair(B) == g1.pair(g2) ** (a * b)
             True

             >>> A.pair(g2) == g1.pair(g2 ** a)
             True
             >>> A.pair(g2) == g1.pair(g2) ** a
             True
        """
        if not type(other) == G2Element:
            raise TypeError("Second parameter should be of type G2Element is {}".format(type(other)))

        res = GTElement()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res

    #
    # Unary operators
    #

    def square(self):
        return native.G1Element.double(self)

    def isquare(self):
        return native.G1Element.idouble(self)

    #
    # Binary operators
    #

    def __mul__(self, other):
        return native.G1Element.__add__(self, other)

    def __imul__(self, other):
        return native.G1Element.__iadd__(self, other)

    def __truediv__(self, other):
        return native.G1Element.__sub__(self, other)

    def __itruediv__(self, other):
        return native.G1Element.__isub__(self, other)

    def __pow__(self, other):
        return native.G1Element.__mul__(self, other)

    def __ipow__(self, other):
        return native.G1Element.__imul__(self, other)

    # Copy documentation from native.GTElement
    square.__doc__ = native.GTElement.square.__doc__.replace("GT", "G1")
    isquare.__doc__ = native.GTElement.isquare.__doc__.replace("GT", "G1")

    __mul__.__doc__ = native.GTElement.__mul__.__doc__.replace("GT", "G1")
    __imul__.__doc__ = native.GTElement.__imul__.__doc__.replace("GT", "G1")

    __truediv__.__doc__ = native.GTElement.__truediv__.__doc__.replace("GT", "G1")
    __itruediv__.__doc__ = native.GTElement.__itruediv__.__doc__.replace("GT", "G1")

    __pow__.__doc__ = native.GTElement.__pow__.__doc__.replace("GT", "G1")
    __ipow__.__doc__ = native.GTElement.__ipow__.__doc__.replace("GT", "G1")

    #
    # Aliases
    #

    mul = __mul__
    imul = __imul__
    div = __truediv__
    idiv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__


class G2(native._G2Base):

    @classmethod
    def _element_type(cls):
        return G2Element

    @classmethod
    def prod(cls, elems):
        """Efficient product of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ G2.generator() ** x for x in [10, 25, 13]]
            >>> G2.prod(elems) ==  G2.generator() ** (10 + 25 + 13)
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
            >>> elems = [ G2.generator() ** x for x in [10, 25, 13]]
            >>> G2.wprod(weights, elems) ==  G2.generator() ** (1 * 10 + 2 * 25 + 3 * 13)
            True
        """
        res = cls.neutral_element()
        for w, el in zip(weights, elems):
            res *= el ** w

        return res

    #
    # Aliases
    #

    @classmethod
    def unity(cls):
        """The unity element

        Alias for :py:meth:`G2.neutral_element`
        """
        return cls.neutral_element()


class G2Element(native._G2ElementBase):
    """Element of the G2 group."""

    group = G2

    #
    # Unary operators
    #

    def square(self):
        return native.G2Element.double(self)

    def isquare(self):
        return native.G2Element.idouble(self)

    #
    # Binary operators
    #

    def __mul__(self, other):
        return native.G2Element.__add__(self, other)

    def __imul__(self, other):
        return native.G2Element.__iadd__(self, other)

    def __truediv__(self, other):
        return native.G2Element.__sub__(self, other)

    def __itruediv__(self, other):
        return native.G2Element.__isub__(self, other)

    def __pow__(self, other):
        return native.G2Element.__mul__(self, other)

    def __ipow__(self, other):
        return native.G2Element.__imul__(self, other)

    # Copy documentation from native.GTElement
    square.__doc__ = native.GTElement.square.__doc__.replace("GT", "G2")
    isquare.__doc__ = native.GTElement.isquare.__doc__.replace("GT", "G2")

    __mul__.__doc__ = native.GTElement.__mul__.__doc__.replace("GT", "G2")
    __imul__.__doc__ = native.GTElement.__imul__.__doc__.replace("GT", "G2")

    __truediv__.__doc__ = native.GTElement.__truediv__.__doc__.replace("GT", "G2")
    __itruediv__.__doc__ = native.GTElement.__itruediv__.__doc__.replace("GT", "G2")

    __pow__.__doc__ = native.GTElement.__pow__.__doc__.replace("GT", "G2")
    __ipow__.__doc__ = native.GTElement.__ipow__.__doc__.replace("GT", "G2")

    #
    # Aliases
    #

    mul = __mul__
    imul = __imul__
    div = __truediv__
    idiv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__


class GT(native.GT):
    """GT group."""

    @classmethod
    def _element_type(cls):
        return GTElement


class GTElement(native.GTElement):
    """GT element."""

    group = GT

