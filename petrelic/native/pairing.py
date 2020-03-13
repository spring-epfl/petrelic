r"""
This module provides a Python wrapper around RELIC's pairings using a native
interface: operations in :py:obj:`petrelic.native.pairings.G1` and
:py:obj:`petrelic.native.pairings.G2` are written additively, whereas operations in
:py:obj:`petrelic.native.pairings.GT` are written multiplicatively.

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
multiply it with the signing key `sk` to obtain a signature:

>>> m = b"Some message"
>>> signature = sk * G1.hash_to_point(m)

Finally, we can use the pairing operator to verify the signature:

>>> signature.pair(G2.generator()) == G1.hash_to_point(m).pair(pk[1])
True

Indeed, the pairing operator is bilinear. For example:

>>> a, b = 13, 29
>>> A = a * G1.generator()
>>> B = b * G2.generator()
>>> A.pair(B) == G1.generator().pair(G2.generator()) ** (a * b)
True

"""

import functools

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other

#
# Utility function
#
def check_same_type(func):
    """Enforce both arguments have same type"""
    @functools.wraps(func)
    def wrapper(a, b):
        if not type(a) == type(b):
            return NotImplemented
        return func(a, b)
    return wrapper


#
# Exceptions
#

class NoAffineCoordinateForECPoint(Exception):
    """Exception raised when an EC point can not be represented as affine coordinates."""
    msg = 'No affine coordinates exists for the given EC point.'


#
# Group pairs
#

class BilinearGroupPair:
    """A bilinear group pair used to wrap the three groups G1, G2, GT."""

    def __init__(self):
        self.gt = GT()
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

class _G1Base(object):
    """All Base G1 methods, will be used in all interfaces
    """

    @classmethod
    def _element_type(cls):
        return G1Element

    @classmethod
    def _new_element(cls):
        return cls._element_type()()

    @classmethod
    def order(cls):
        """Return the order of the group as a Bn large integer.

        Example:
            >>> generator = G1.generator()
            >>> neutral = G1.neutral_element()
            >>> order = G1.order()
            >>> order * generator == neutral
            True
        """
        order = Bn()
        _C.g1_get_ord(order.bn)
        return order

    @classmethod
    def generator(cls):
        """Return generator of the group.

        Example:
            >>> generator = G1.generator()
            >>> neutral = G1.neutral_element()
            >>> generator + neutral == generator
            True
        """
        generator = cls._new_element()
        _C.g1_get_gen(generator.pt)
        generator._is_gen = True
        return generator

    @classmethod
    def neutral_element(cls):
        """Return the neutral element of the group G1.

        In this case, the point at infinity.

        Example:
            >>> generator = G1.generator()
            >>> neutral = G1.neutral_element()
            >>> generator + neutral == generator
            True
        """
        neutral = cls._new_element()
        _C.g1_set_infty(neutral.pt)
        return neutral

    @classmethod
    def hash_to_point(cls, hinput):
        """Return group element obtained by hashing the input

        Example:
            >>> elem = G1.hash_to_point(b"foo")
            >>> elem.is_valid()
            True
        """
        res = cls._new_element()
        _C.g1_map(res.pt, hinput, len(hinput))
        return res

class G1(_G1Base):
    """The G1 group."""

    @classmethod
    def sum(cls, elems):
        """Efficient sum of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ x * G1.generator() for x in [10, 25, 13]]
            >>> G1.sum(elems) ==  (10 + 25 + 13) * G1.generator()
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
            >>> elems = [ x * G1.generator() for x in [10, 25, 13]]
            >>> G1.wsum(weights, elems) ==  (1 * 10 + 2 * 25 + 3 * 13) * G1.generator()
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
        """The point at infinity.

        Alias for :py:meth:`G1.neutral_element`
        """
        return cls.neutral_element()


class _G1ElementBase(object):
    def __init__(self):
        """Initialize a new element of G1."""
        self.pt = _FFI.new("g1_t")
        self._is_gen = False
        _C.g1_null(self.pt)
        _C.g1_new(self.pt)

    def __copy__(self):
        """Clone an element of G1."""
        copy = self.__class__()
        _C.g1_copy(copy.pt, self.pt)
        copy._is_gen = self._is_gen
        return copy

    #
    # Misc
    #

    def is_valid(self):
        """Check if the element indeed lies on the curve.

        Example:
            >>> elem = G1.hash_to_point(b"foo")
            >>> elem.is_valid()
            True
        """
        return bool(_C.g1_is_valid(self.pt))

    def is_neutral_element(self):
        """Check if the object is the neutral element of G1.

        Example:
            >>> generator = G1.generator()
            >>> order = G1.order()
            >>> elem = order * generator
            >>> elem.is_neutral_element()
            True
        """
        _C.g1_norm(self.pt, self.pt)
        return bool(_C.g1_is_infty(self.pt))

    def get_affine_coordinates(self):
        """Return the affine coordinates (x,y) of this EC Point.

        Example:
            >>> generator = G1.generator()
            >>> x, y = generator.get_affine_coordinates()
            >>> x
            Bn(3685416753713387016781088315183077757961620795782546409894578378688607592378376318836054947676345821548104185464507)
            >>> y
            Bn(1339506544944476473020471379941921221584933875938349620426543736416511423956333506472724655353366534992391756441569)
        """
        if self.is_neutral_element():
            raise NoAffineCoordinateForECPoint()

        x = Bn()
        y = Bn()
        _C.fp_prime_back(x.bn, self.pt[0].x)
        _C.fp_prime_back(y.bn, self.pt[0].y)

        return x, y

    def pair(self, other):
        """Pair element with another element in G2

        Computes the bilinear pairing between self and another element in
        :py:obj:`petrelic.native.pairing.G2`.

        Examples:
             >>> g1, g2 = G1.generator(), G2.generator()
             >>> a, b = 10, 50
             >>> A, B = a * g1, b * g2
             >>> A.pair(B) == g1.pair(g2) ** (a * b)
             True

             >>> A.pair(g2) == g1.pair(a * g2)
             True
             >>> A.pair(g2) == g1.pair(g2) ** a
             True
        """
        if not type(other) == G2Element:
            raise TypeError("Second parameter should be of type G2Element is {}".format(type(other)))

        res = GTElement()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res

    def __hash__(self):
        """Hash function used internally by Python."""
        return self.to_binary().__hash__()

    def __repr__(self):
        """String representation of the element of G1."""
        pt_hex = self.to_binary().hex()
        return 'G1Element({})'.format(pt_hex)

    #
    # Serialization
    #

    @classmethod
    def from_binary(cls, sbin):
        """Deserialize a binary representation of the element of G1.

        Example:
            >>> generator = G1.generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = G1Element.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        elem = cls()
        elem._is_gen = False
        _C.g1_read_bin(elem.pt, sbin, len(sbin))
        return elem

    def to_binary(self, compressed=True):
        """Serialize the element of G1 into a binary representation.

        Example:
            >>> generator = G1.generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = G1Element.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        flag = 1 if compressed else 0
        length = _C.g1_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.g1_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    #
    # Unary operators
    #

    def inverse(self):
        """Return the inverse of the element.

        Examples:
            >>> a = 30
            >>> elem = a * G1.generator()
            >>> -elem == elem.inverse()
            True
            >>> elem.inverse() == (G1.order() - a) * G1.generator()
            True
        """
        res = self.__class__()
        _C.g1_neg(res.pt, self.pt)
        return res

    def iinverse(self):
        """Inplace inverse of the current element

        Examples:
            >>> a = 30
            >>> elem1 = a * G1.generator()
            >>> elem2 = a * G1.generator()
            >>> _ = elem1.iinverse()
            >>> elem1 == elem2.inverse()
            True
        """
        _C.g1_neg(self.pt, self.pt)
        return self


    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check point equality."""
        if not isinstance(other, self.__class__):
            return False

        return _C.g1_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points are different."""
        if not isinstance(other, self.__class__):
            return True

        return _C.g1_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    eq = __eq__
    ne = __ne__


class G1Element(_G1ElementBase):
    """Element of the G1 group."""

    group = G1

    def double(self):
        """Return double of the current element

        Example:
            >>> generator = G1.generator()
            >>> elem = generator.double()
            >>> elem == 2 * generator
            True
        """
        res = self.__class__()
        _C.g1_dbl(res.pt, self.pt)
        return res

    def idouble(self):
        """Inplace double the current element.

        Example:
            >>> generator = G1.generator()
            >>> elem = G1.generator()
            >>> _ = elem.idouble()
            >>> elem == 2 * generator
            True
        """
        self._is_gen = False
        _C.g1_dbl(self.pt, self.pt)
        return self


    #
    # Binary operators
    #

    @check_same_type
    def __add__(self, other):
        """Add two points together.

        This method is aliased by `a + b`.

        Examples:
            >>> a = 10 * G1.generator()
            >>> b = 40 * G1.generator()
            >>> a + b == 50 * G1.generator()
            True
            >>> a.add(b) == 50 * G1.generator()
            True
        """
        res = self.__class__()
        _C.g1_add(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __iadd__(self, other):
        """Inplace add another point.

        Examples:
            >>> a = 10 * G1.generator()
            >>> b = 10 * G1.generator()
            >>> a += 3 * G1.generator()
            >>> _ = b.iadd(3 * G1.generator())
            >>> a == b
            True
            >>> a == 13 * G1.generator()
            True
        """
        self._is_gen = False
        _C.g1_add(self.pt, self.pt, other.pt)
        return self

    @check_same_type
    def __sub__(self, other):
        """Substract two points

        This method is aliased by `a - b`.

        Examples:
            >>> a = 50 * G1.generator()
            >>> b = 13 * G1.generator()
            >>> a - b == 37 * G1.generator()
            True
            >>> a.sub(b) == 37 * G1.generator()
            True
        """
        res = self.__class__()
        _C.g1_sub(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __isub__(self, other):
        """Inplace substract another point.

        Examples:
            >>> a = 10 * G1.generator()
            >>> b = 10 * G1.generator()
            >>> a -= 3 * G1.generator()
            >>> _ = b.isub(3 * G1.generator())
            >>> a == b
            True
            >>> a == 7 * G1.generator()
            True
        """

        self._is_gen = False
        _C.g1_sub(self.pt, self.pt, other.pt)
        return self

    @force_Bn_other
    def __mul__(self, other):
        """Multiply point by a scalar

        This method is aliased by `n * pt`.

        Examples:
            >>> g = G1.generator()
            >>> g + g == 2 * g
            True
        """
        res = self.__class__()
        if self._is_gen:
            _C.g1_mul_gen(res.pt, other.bn)
        else:
            _C.g1_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __rmul__(self, other):
        res = self.__class__()
        if self._is_gen:
            _C.g1_mul_gen(res.pt, other.bn)
        else:
            _C.g1_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __imul__(self, other):
        """Inplace point multiplication by a scalar

        Examples:
            >>> a = G1.generator()
            >>> b = G1.generator()
            >>> a *= 10
            >>> _ = b.imul(10)
            >>> a == b
            True
            >>> a == 10 * G1.generator()
            True
        """
        if self._is_gen:
            _C.g1_mul_gen(self.pt, other.bn)
            self._is_gen = False
        else:
            _C.g1_mul(self.pt, self.pt, other.bn)
        return self

    #
    # Aliases
    #

    is_infinity = _G1ElementBase.is_neutral_element
    __neg__ = _G1ElementBase.inverse

    neg = __neg__
    add = __add__
    iadd = __iadd__
    sub = __sub__
    isub = __isub__
    mul = __mul__
    imul = __imul__


class _G2Base(object):
    """Internal base class for G2"""

    @classmethod
    def _element_type(cls):
        return G2Element

    @classmethod
    def _new_element(cls):
        return cls._element_type()()


    @classmethod
    def order(cls):
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = G2.generator()
            >>> neutral = G2.neutral_element()
            >>> order = G2.order()
            >>> order * generator == neutral
            True
        """
        order = Bn()
        _C.g2_get_ord(order.bn)
        return order

    @classmethod
    def generator(cls):
        """Return generator of the group.

        Example:
            >>> generator = G2.generator()
            >>> neutral = G2.neutral_element()
            >>> generator + neutral == generator
            True
        """
        generator = cls._new_element()
        _C.g2_get_gen(generator.pt)
        return generator

    @classmethod
    def neutral_element(cls):
        """Return the neutral element of the group G2.

        In this case, the point at infinity.

        Example:
            >>> generator = G2.generator()
            >>> neutral = G2.neutral_element()
            >>> generator + neutral == generator
            True
        """
        neutral = cls._new_element()
        _C.g2_set_infty(neutral.pt)
        return neutral

    @classmethod
    def hash_to_point(cls, hinput):
        """Return group element obtained by hashing the input

        Example:
            >>> elem = G2.hash_to_point(b"foo")
            >>> elem.is_valid()
            True
        """
        res = cls()._new_element()
        _C.g2_map(res.pt, hinput, len(hinput))
        return res


class G2(_G2Base):
    """G2 group."""

    @classmethod
    def sum(cls, elems):
        """Efficient sum of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ x * G2.generator() for x in [10, 25, 13]]
            >>> G2.sum(elems) ==  (10 + 25 + 13) * G2.generator()
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
            >>> elems = [ x * G2.generator() for x in [10, 25, 13]]
            >>> G2.wsum(weights, elems) ==  (1 * 10 + 2 * 25 + 3 * 13) * G2.generator()
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
        """The point at infinity.

        Alias for :py:meth:`G1.neutral_element`
        """
        return cls.neutral_element()


class _G2ElementBase(object):
    def __init__(self):
        """Initialize a new element of G2."""
        self.pt = _FFI.new("g2_t")
        _C.g2_null(self.pt)
        _C.g2_new(self.pt)

    def __copy__(self):
        """Clone an element of G2."""
        copy = self.__class__()
        _C.g2_copy(copy.pt, self.pt)
        return copy

    #
    # Misc
    #

    def is_valid(self):
        return bool(_C.g2_is_valid(self.pt))

    def is_neutral_element(self):
        _C.g2_norm(self.pt, self.pt)
        return bool(_C.g2_is_infty(self.pt))

    def __hash__(self):
        """Hash function used internally by Python."""
        return self.to_binary().__hash__()

    def __repr__(self):
        """String representation of the element of G2."""
        pt_hex = self.to_binary().hex()
        return 'G2Element({})'.format(pt_hex)


    #
    # Serialization
    #

    @classmethod
    def from_binary(cls, sbin):
        """Deserialize a binary representation of the element of G2.

        Example:
            >>> generator = G2.generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = G2Element.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        elem = cls()
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

    def inverse(self):
        res = self.__class__()
        _C.g2_neg(res.pt, self.pt)
        return res

    def iinverse(self):
        _C.g2_neg(self.pt, self.pt)
        return self

    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points on the EC are equal."""
        if not isinstance(other, self.__class__):
            return False

        return _C.g2_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
        if not isinstance(other, self.__class__):
            return True

        return _C.g2_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    eq = __eq__
    ne = __ne__

    # Copy documentation from G1Element
    to_binary.__doc__ = G1Element.to_binary.__doc__.replace("G1", "G2")

    is_valid.__doc__ = G1Element.is_valid.__doc__.replace("G1", "G2")
    is_neutral_element.__doc__ = G1Element.is_neutral_element.__doc__.replace("G1", "G2")
    inverse.__doc__ = G1Element.inverse.__doc__.replace("G1", "G2")
    iinverse.__doc__ = G1Element.iinverse.__doc__.replace("G1", "G2")



class G2Element(_G2ElementBase):
    """Element of the G2 group."""

    #
    # Unary operators
    #

    def double(self):
        res = self.__class__()
        _C.g2_dbl(res.pt, self.pt)
        return res

    def idouble(self):
        _C.g2_dbl(self.pt, self.pt)
        return self

    #
    # Binary operators
    #

    @check_same_type
    def __add__(self, other):
        res = self.__class__()
        _C.g2_add(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __iadd__(self, other):
        _C.g2_add(self.pt, self.pt, other.pt)
        return self

    @check_same_type
    def __sub__(self, other):
        res = self.__class__()
        _C.g2_sub(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __isub__(self, other):
        _C.g2_sub(self.pt, self.pt, other.pt)
        return self

    @force_Bn_other
    def __mul__(self, other):
        res = self.__class__()
        _C.g2_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __rmul__(self, other):
        res = self.__class__()
        _C.g2_mul(res.pt, self.pt, other.bn)
        return res

    @force_Bn_other
    def __imul__(self, other):
        _C.g2_mul(self.pt, self.pt, other.bn)
        return self

    # Copy documentation from G1Element
    double.__doc__ = G1Element.double.__doc__.replace("G1", "G2")
    idouble.__doc__ = G1Element.idouble.__doc__.replace("G1", "G2")

    __add__.__doc__ = G1Element.__add__.__doc__.replace("G1", "G2")
    __iadd__.__doc__ = G1Element.__add__.__doc__.replace("G1", "G2")

    __sub__.__doc__ = G1Element.__sub__.__doc__.replace("G1", "G2")
    __isub__.__doc__ = G1Element.__isub__.__doc__.replace("G1", "G2")

    __mul__.__doc__ = G1Element.__mul__.__doc__.replace("G1", "G2")
    __imul__.__doc__ = G1Element.__imul__.__doc__.replace("G1", "G2")

    #
    # Aliases
    #

    is_infinity = _G2ElementBase.is_neutral_element
    __neg__ = _G2ElementBase.inverse

    neg = __neg__
    add = __add__
    iadd = __iadd__
    sub = __sub__
    isub = __isub__
    mul = __mul__
    imul = __imul__


class _GTBase(object):
    """Internal base class for GT"""

    @classmethod
    def _element_type(cls):
        return GTElement

    @classmethod
    def _new_element(cls):
        return cls._element_type()()


    @classmethod
    def order(cls):
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = GT.generator()
            >>> neutral = GT.neutral_element()
            >>> order = GT.order()
            >>> generator ** order == neutral
            True
        """
        order = Bn()
        _C.gt_get_ord(order.bn)
        return order

    @classmethod
    def generator(cls):
        """Return generator of the EC group.

        Example:
            >>> generator = GT.generator()
            >>> neutral = GT.neutral_element()
            >>> generator * neutral == generator
            True
        """
        generator = cls._new_element()
        _C.gt_get_gen(generator.pt)
        return generator

    @classmethod
    def neutral_element(cls):
        """Return the neutral element of the group GT.
        In this case, the unity point.

        Example:
            >>> generator = GT.generator()
            >>> neutral = GT.neutral_element()
            >>> generator * neutral == generator
            True
        """
        neutral = cls._new_element()
        _C.gt_set_unity(neutral.pt)
        return neutral

class GT(_GTBase):
    """GT group."""

    @classmethod
    def prod(cls, elems):
        """Efficient product of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ GT.generator() ** x for x in [10, 25, 13]]
            >>> GT.prod(elems) ==  GT.generator() ** (10 + 25 + 13)
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
            >>> elems = [ GT.generator() ** x for x in [10, 25, 13]]
            >>> GT.wprod(weights, elems) ==  GT.generator() ** (1 * 10 + 2 * 25 + 3 * 13)
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
        """The unity elements

        Alias for :py:meth:`GT.neutral_element`
        """
        return cls.neutral_element()


class _GTElementBase(object):

    def __init__(self):
        """Initialize a new element of GT."""
        self.pt = _FFI.new("gt_t")
        _C.gt_null(self.pt)
        _C.gt_new(self.pt)

    def __copy__(self):
        """Clone an element of GT."""
        copy = self.__class__()
        _C.gt_copy(copy.pt, self.pt)
        return copy

    #
    # Misc
    #

    def is_valid(self):
        """Check if the element is in the group

        Example:
            >>> elem = GT.generator() ** 1337
            >>> elem.is_valid()
            True
        """
        # TODO: gt_is_valid does not accept unity.
        if bool(_C.gt_is_unity(self.pt)):
            return True

        return bool(_C.gt_is_valid(self.pt))

    def is_neutral_element(self):
        """Check if the object is the neutral element of GT.

        Example:
            >>> generator = GT.generator()
            >>> order = GT.order()
            >>> elem = generator ** order
            >>> elem.is_neutral_element()
            True
        """
        return bool(_C.gt_is_unity(self.pt))

    def __hash__(self):
        """Hash function used internally by Python."""
        return self.to_binary().__hash__()

    def __repr__(self):
        """String representation of the element of G2."""
        pt_hex = self.to_binary().hex()
        return 'GTElement({})'.format(pt_hex)

    #
    # Serialization
    #

    @classmethod
    def from_binary(cls, sbin):
        """Deserialize a binary representation of the element of GT.

        Example:
            >>> generator = GT.generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = GTElement.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        ret = cls()
        _C.gt_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def to_binary(self, compressed=True):
        flag = int(compressed)
        length = _C.gt_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.gt_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    to_binary.__doc__ = G1Element.to_binary.__doc__.replace("G1", "GT")


    #
    # Unary operators
    #

    def inverse(self):
        """Return the inverse of the element.

        Examples:
            >>> a = 30
            >>> elem = GT.generator() ** a
            >>> elem.inverse() == GT.generator() ** (G1.order() - a)
            True
        """
        res = self.__class__()
        _C.gt_inv(res.pt, self.pt)
        return res

    def iinverse(self):
        """Inplace inverse of the current element

        Examples:
            >>> a = 30
            >>> elem1 = GT.generator() ** a
            >>> elem2 = GT.generator() ** a
            >>> _ = elem1.iinverse()
            >>> elem1 == elem2.inverse()
            True
        """
        _C.gt_inv(self.pt, self.pt)
        return self

    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points are equal."""
        if not isinstance(other, self.__class__):
            return False

        return _C.gt_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
        if not isinstance(other, self.__class__):
            return True

        return _C.gt_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    eq = __eq__
    ne = __ne__


class GTElement(_GTElementBase):
    """GT element."""

    group = GT


    def square(self):
        """Return the square of the current element

        Example:
            >>> generator = GT.generator()
            >>> elem = generator.square()
            >>> elem == generator ** 2
            True
        """
        res = self.__class__()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def isquare(self):
        """Inplace square of the current element.

        Example:
            >>> elem = GT.generator()
            >>> _ = elem.isquare()
            >>> elem == GT.generator() ** 2
            True
        """
        _C.gt_sqr(self.pt, self.pt)
        return self


    #
    # Binary operators
    #

    @check_same_type
    def __mul__(self, other):
        """Multiply two elements

        This method is aliased by `a * b`.

        Examples:
            >>> a = GT.generator() ** 10
            >>> b = GT.generator() ** 40
            >>> a * b == GT.generator() ** 50
            True
            >>> a.mul(b) == GT.generator() ** 50
            True
        """
        res = self.__class__()
        _C.gt_mul(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __imul__(self, other):
        """Inplace multiplication by another element

        Examples:
            >>> a = GT.generator() ** 10
            >>> b = GT.generator() ** 10
            >>> a *= GT.generator() ** 3
            >>> _ = b.imul(GT.generator() ** 3)
            >>> a == b
            True
            >>> a == GT.generator() ** 13
            True
        """
        _C.gt_mul(self.pt, self.pt, other.pt)
        return self

    @check_same_type
    def __truediv__(self, other):
        """Divide two points

        This method is aliased by `a / b` and `a // b`.

        Examples:
            >>> a = GT.generator() ** 50
            >>> b = GT.generator() ** 13
            >>> a / b == GT.generator() ** 37
            True
            >>> a // b == GT.generator() ** 37
            True
            >>> a.div(b) == GT.generator() ** 37
            True
        """
        res = other.inverse()
        _C.gt_mul(res.pt, self.pt, res.pt)
        return res

    @check_same_type
    def __itruediv__(self, other):
        """Inplace division by another point

        Examples:
            >>> a = GT.generator() ** 10
            >>> b = GT.generator() ** 10
            >>> a /= GT.generator() ** 3
            >>> _ = b.idiv(GT.generator() ** 3)
            >>> a == b
            True
            >>> a == GT.generator() ** 7
            True
        """
        other_inv = other.inverse()
        _C.gt_mul(self.pt, self.pt, other_inv.pt)
        return self

    @force_Bn_other
    def __pow__(self, other):
        """Raise element to the power of a scalar

        This method is aliased by `el ** n`.

        Examples:
            >>> g = GT.generator()
            >>> g * g == g ** 2
            True
            >>> g * g == g.pow(2)
            True
        """
        res = self.__class__()
        exponent = other.mod(self.group.order())
        _C.gt_exp(res.pt, self.pt, exponent.bn)
        return res

    @force_Bn_other
    def __ipow__(self, other):
        """Inplace raise element to the power of a scalar

        Examples:
            >>> g = GT.generator()
            >>> a = GT.generator()
            >>> _ = a.ipow(3)
            >>> g * g * g == a
            True
        """
        exponent = other.mod(self.group.order())
        _C.gt_exp(self.pt, self.pt, exponent.bn)
        return self


    #
    # Aliases
    #

    is_unity = _GTElementBase.is_neutral_element

    mul = __mul__
    imul = __imul__
    div = __truediv__
    idiv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__
