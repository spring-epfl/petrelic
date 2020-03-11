r"""
A native Python wrapper around RELIC's pairings

This module provides a Python wrapper around RELIC's pairings using a native
interface: operations in :py:obj:`petrelic.pairings.G1` and
:py:obj:`petrelic.pairings.G2` are written additively, whereas operations in
:py:obj:`petrelic.pairings.Gt` are written multiplicatively.

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

"""Clean API of the petrelic library.
"""

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other

#
# Utility function
#
def check_same_type(func):
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
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group Gt.
    """

    def __init__(self):
        self.gt = Gt()
        self.g1 = G1()
        self.g2 = G2()

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, Gt.
        """
        return self.g1, self.g2, self.gt


#
# Group and Elements
#

class G1:
    """G1 group."""

    @classmethod
    def _element_type(cls):
        return G1Element

    @classmethod
    def _new_element(cls):
        return cls._element_type()()

    @classmethod
    def order(cls):
        """Return the order of the EC group as a Bn large integer.

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
        """Return generator of the EC group.

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
        In this case, a point at infinity.

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

    infinity = neutral_element


class G1Element():
    """Element of the G1 group."""

    group = G1

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
        """Check if the data of this object is indeed a point on the EC.

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

    def double(self):
        """Return an element which is the double of the current one.

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
        """Double the current element.

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
        res = GtElement()
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

    def __neg__(self):
        """Return the inverse of the element of the G1."""
        res = self.__class__()
        _C.g1_neg(res.pt, self.pt)
        return res

    def iinverse(self):
        """Inplace inverse"""
        _C.g1_neg(self.pt, self.pt)
        return self

    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points on the EC are equal."""
        if not isinstance(other, self.__class__):
            return False

        return _C.g1_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
        if not isinstance(other, self.__class__):
            return True

        return _C.g1_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Binary operators
    #

    @check_same_type
    def __add__(self, other):
        res = self.__class__()
        _C.g1_add(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __iadd__(self, other):
        self._is_gen = False
        _C.g1_add(self.pt, self.pt, other.pt)
        return self

    @check_same_type
    def __sub__(self, other):
        res = self.__class__()
        _C.g1_sub(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __isub__(self, other):
        self._is_gen = False
        _C.g1_sub(self.pt, self.pt, other.pt)
        return self

    @force_Bn_other
    def __mul__(self, other):
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
        if self._is_gen:
            _C.g1_mul_gen(self.pt, other.bn)
            self._is_gen = False
        else:
            _C.g1_mul(self.pt, self.pt, other.bn)
        return self

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    is_infinity = is_neutral_element
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


class G2:
    """G2 group."""

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
        """Return generator of the EC group.

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
        In this case, a point at infinity.

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

    @classmethod
    def hash_to_point(cls, hinput):
        return cls._element_type().from_hashed_bytes(hinput)

    #
    # Aliases
    #

    infinity = neutral_element


class G2Element():
    """G2 element."""

    group = G2

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

    @classmethod
    def from_hashed_bytes(cls, hinput):
        """Generate an point on the EC from a hashed byte string.

        Example:
            >>> elem = G2Element.from_hashed_bytes(b"foo")
            >>> elem.is_valid()
            True
        """
        res = cls()
        _C.g2_map(res.pt, hinput, len(hinput))
        return res

    def is_valid(self):
        """Check if the data of this object is indeed a point on the EC.

        Example:
            >>> elem = G2Element.from_hashed_bytes(b"foo")
            >>> elem.is_valid()
            True
        """
        return bool(_C.g2_is_valid(self.pt))

    def is_neutral_element(self):
        """Check if the object is the neutral element of G2.

        Example:
            >>> generator = G2.generator()
            >>> order = G2.order()
            >>> elem = order * generator
            >>> elem.is_neutral_element()
            True
        """
        _C.g2_norm(self.pt, self.pt)
        return bool(_C.g2_is_infty(self.pt))

    def double(self):
        """Return an element which is the double of the current one.

        Example:
            >>> generator = G2.generator()
            >>> elem = generator.double()
            >>> elem == 2 * generator
            True
        """
        res = self.__class__()
        _C.g2_dbl(res.pt, self.pt)
        return res

    def idouble(self):
        """Double the current element.

        Example:
            >>> generator = G2.generator()
            >>> elem = G2.generator().idouble()
            >>> elem == 2 * generator
            True
        """
        _C.g2_dbl(self.pt, self.pt)
        return self

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
        """Serialize the element of G2 into a binary representation.

        Example:
            >>> generator = G2.generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = G2Element.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        flag = int(compressed)
        length = _C.g2_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.g2_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    #
    # Unary operators
    #

    def __neg__(self):
        """Return the inverse of the element of G2."""
        res = self.__class__()
        _C.g2_neg(res.pt, self.pt)
        return res

    def iinverse(self):
        """Inplace inverse"""
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

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    is_infinity = is_neutral_element
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


class Gt:
    """Gt group."""

    @classmethod
    def _element_type(cls):
        return GtElement

    @classmethod
    def _new_element(cls):
        return cls._element_type()()


    @classmethod
    def order(cls):
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = Gt.generator()
            >>> neutral = Gt.neutral_element()
            >>> order = Gt.order()
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
            >>> generator = Gt.generator()
            >>> neutral = Gt.neutral_element()
            >>> generator * neutral == generator
            True
        """
        generator = cls._new_element()
        _C.gt_get_gen(generator.pt)
        return generator

    @classmethod
    def neutral_element(cls):
        """Return the neutral element of the group Gt.
        In this case, the unity point.

        Example:
            >>> generator = Gt.generator()
            >>> neutral = Gt.neutral_element()
            >>> generator * neutral == generator
            True
        """
        neutral = cls._new_element()
        _C.gt_set_unity(neutral.pt)
        return neutral

    @classmethod
    def prod(cls, elems):
        """Efficient product of a number of elements

        In the current implementation this function is not optimized.

        Example:
            >>> elems = [ Gt.generator() ** x for x in [10, 25, 13]]
            >>> Gt.prod(elems) ==  Gt.generator() ** (10 + 25 + 13)
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
            >>> elems = [ Gt.generator() ** x for x in [10, 25, 13]]
            >>> Gt.wprod(weights, elems) ==  Gt.generator() ** (1 * 10 + 2 * 25 + 3 * 13)
            True
        """
        res = cls.neutral_element()
        for w, el in zip(weights, elems):
            res *= el ** w

        return res

    #
    # Aliases
    #

    get_unity = neutral_element


class GtElement():
    """Gt element."""

    group = Gt

    def __init__(self):
        """Initialize a new element of Gt."""
        self.pt = _FFI.new("gt_t")
        _C.gt_null(self.pt)
        _C.gt_new(self.pt)

    def __copy__(self):
        """Clone an element of Gt."""
        copy = self.__class__()
        _C.gt_copy(copy.pt, self.pt)
        return copy

    #
    # Misc
    #

    def is_valid(self):
        """Check if the data of this object is indeed a point on the EC.

        Example:
            >>> elem = Gt.generator()
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
            >>> generator = Gt.generator()
            >>> order = Gt.order()
            >>> elem = generator ** order
            >>> elem.is_neutral_element()
            True
        """
        return bool(_C.gt_is_unity(self.pt))

    def inverse(self):
        """Return the inverse of the element of Gt."""
        res = self.__class__()
        _C.gt_inv(res.pt, self.pt)
        return res

    def iinverse(self):
        """Inverse the element of Gt."""
        _C.gt_inv(self.pt, self.pt)
        return self

    def square(self):
        """Return an element which is the square of the current one.

        Example:
            >>> generator = Gt.generator()
            >>> elem = generator.square()
            >>> elem == generator ** 2
            True
        """
        res = self.__class__()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def isquare(self):
        """Double the current element.

        Example:
            >>> generator = Gt.generator()
            >>> elem = Gt.generator().isquare()
            >>> elem == generator ** 2
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

    @classmethod
    def from_binary(cls, sbin):
        """Deserialize a binary representation of the element of Gt.

        Example:
            >>> generator = Gt.generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = GtElement.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        ret = cls()
        _C.gt_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def to_binary(self, compressed=True):
        """Serialize the element of Gt into a binary representation.

        Example:
            >>> generator = Gt.generator()
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
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points on the EC are equal."""
        if not isinstance(other, self.__class__):
            return False

        return _C.gt_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
        if not isinstance(other, self.__class__):
            return True

        return _C.gt_cmp(self.pt, other.pt) != _C.CONST_RLC_EQ

    #
    # Binary operators
    #

    @check_same_type
    def __mul__(self, other):
        res = self.__class__()
        _C.gt_mul(res.pt, self.pt, other.pt)
        return res

    @check_same_type
    def __imul__(self, other):
        _C.gt_mul(self.pt, self.pt, other.pt)
        return self

    @check_same_type
    def __truediv__(self, other):
        res = other.inverse()
        _C.gt_mul(res.pt, self.pt, res.pt)
        return res

    @check_same_type
    def __itruediv__(self, other):
        other_inv = other.inverse()
        _C.gt_mul(self.pt, self.pt, other_inv.pt)
        return self

    @force_Bn_other
    def __pow__(self, other):
        res = self.__class__()
        exponent = other.mod(self.group.order())
        _C.gt_exp(res.pt, self.pt, exponent.bn)
        return res

    @force_Bn_other
    def __ipow__(self, other):
        exponent = other.mod(self.group.order())
        _C.gt_exp(self.pt, self.pt, exponent.bn)
        return self

    #
    # Aliases
    #

    __deepcopy__ = __copy__
    is_unity = is_neutral_element
    eq = __eq__
    ne = __ne__
    mul = __mul__
    imul = __imul__
    truediv = __truediv__
    itruediv = __itruediv__
    __floordiv__ = __truediv__
    __ifloordiv__ = __itruediv__
    pow = __pow__
    ipow = __ipow__
