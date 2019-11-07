
"""Clean API of the petrelic library.
"""

from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other

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

    @staticmethod
    def get_order():
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = G1.get_generator()
            >>> neutral = G1.get_neutral_element()
            >>> order = G1.get_order()
            >>> order * generator == neutral
            True
        """
        order = Bn()
        _C.g1_get_ord(order.bn)
        return order

    @staticmethod
    def get_generator():
        """Return generator of the EC group.

        Example:
            >>> generator = G1.get_generator()
            >>> neutral = G1.get_neutral_element()
            >>> generator + neutral == generator
            True
        """
        generator = G1Element()
        _C.g1_get_gen(generator.pt)
        generator._is_gen = True
        return generator

    @staticmethod
    def get_neutral_element():
        """Return the neutral element of the group G1.
        In this case, a point at infinity.

        Example:
            >>> generator = G1.get_generator()
            >>> neutral = G1.get_neutral_element()
            >>> generator + neutral == generator
            True
        """
        neutral = G1Element()
        _C.g1_set_infty(neutral.pt)
        return neutral

    @staticmethod
    def hash_to_point(hinput):
        return G1Element.from_hashed_bytes(hinput)

    @staticmethod
    def sum(elems):
        return sum(elems)

    @staticmethod
    def wsum(weights, elems):
        res = G1.get_neutral_element()
        for w, el in zip(weights, elems):
            res += w * el

        return res


    #
    # Aliases
    #

    get_infinity = get_neutral_element
    generator = get_generator
    order = get_order


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
        copy = G1Element()
        _C.g1_copy(copy.pt, self.pt)
        copy._is_gen = self._is_gen
        return copy

    #
    # Misc
    #

    @staticmethod
    def from_hashed_bytes(hinput):
        """Generate an point on the EC from a hashed byte string.

        Example:
            >>> elem = G1Element.from_hashed_bytes(b"foo")
            >>> elem.is_valid()
            True
        """
        res = G1Element()
        _C.g1_map(res.pt, hinput, len(hinput))
        return res

    def is_valid(self):
        """Check if the data of this object is indeed a point on the EC.

        Example:
            >>> elem = G1Element.from_hashed_bytes(b"foo")
            >>> elem.is_valid()
            True
        """
        return bool(_C.g1_is_valid(self.pt))

    def is_neutral_element(self):
        """Check if the object is the neutral element of G1.

        Example:
            >>> generator = G1.get_generator()
            >>> order = G1.get_order()
            >>> elem = order * generator
            >>> elem.is_neutral_element()
            True
        """
        _C.g1_norm(self.pt, self.pt)
        return bool(_C.g1_is_infty(self.pt))

    def double(self):
        """Return an element which is the double of the current one.

        Example:
            >>> generator = G1.get_generator()
            >>> elem = generator.double()
            >>> elem == 2 * generator
            True
        """
        res = G1Element()
        _C.g1_dbl(res.pt, self.pt)
        return res

    def idouble(self):
        """Double the current element.

        Example:
            >>> generator = G1.get_generator()
            >>> elem = G1.get_generator().idouble()
            >>> elem == 2 * generator
            True
        """
        self._is_gen = False
        _C.g1_dbl(self.pt, self.pt)
        return self

    def get_affine_coordinates(self):
        """Return the affine coordinates (x,y) of this EC Point.

        Example:
            >>> generator = G1.get_generator()
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

    @staticmethod
    def from_binary(sbin):
        """Deserialize a binary representation of the element of G1.

        Example:
            >>> generator = G1.get_generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = G1Element.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        elem = G1Element()
        elem._is_gen = False
        _C.g1_read_bin(elem.pt, sbin, len(sbin))
        return elem

    def to_binary(self, compressed=True):
        """Serialize the element of G1 into a binary representation.

        Example:
            >>> generator = G1.get_generator()
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
        res = G1Element()
        _C.g1_neg(res.pt, self.pt)
        return res

    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points on the EC are equal."""
        if not isinstance(other, G1Element):
            return False

        return _C.g1_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
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

    @staticmethod
    def get_order():
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = G2.get_generator()
            >>> neutral = G2.get_neutral_element()
            >>> order = G2.get_order()
            >>> order * generator == neutral
            True
        """
        order = Bn()
        _C.g2_get_ord(order.bn)
        return order

    @staticmethod
    def get_generator():
        """Return generator of the EC group.

        Example:
            >>> generator = G2.get_generator()
            >>> neutral = G2.get_neutral_element()
            >>> generator + neutral == generator
            True
        """
        generator = G2Element()
        _C.g2_get_gen(generator.pt)
        return generator

    @staticmethod
    def get_neutral_element():
        """Return the neutral element of the group G2.
        In this case, a point at infinity.

        Example:
            >>> generator = G2.get_generator()
            >>> neutral = G2.get_neutral_element()
            >>> generator + neutral == generator
            True
        """
        neutral = G2Element()
        _C.g2_set_infty(neutral.pt)
        return neutral

    @staticmethod
    def sum(elems):
        return sum(elems)

    @staticmethod
    def wsum(weights, elems):
        res = G2.get_neutral_element()
        for w, el in zip(weights, elems):
            res += w * el

        return res


    @staticmethod
    def hash_to_point(hinput):
        return G2Element.from_hashed_bytes(hinput)

    #
    # Aliases
    #

    get_infinity = get_neutral_element
    generator = get_generator
    order = get_order


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
        copy = G2Element()
        _C.g2_copy(copy.pt, self.pt)
        return copy

    #
    # Misc
    #

    @staticmethod
    def from_hashed_bytes(hinput):
        """Generate an point on the EC from a hashed byte string.

        Example:
            >>> elem = G2Element.from_hashed_bytes(b"foo")
            >>> elem.is_valid()
            True
        """
        res = G2Element()
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
            >>> generator = G2.get_generator()
            >>> order = G2.get_order()
            >>> elem = order * generator
            >>> elem.is_neutral_element()
            True
        """
        _C.g2_norm(self.pt, self.pt)
        return bool(_C.g2_is_infty(self.pt))

    def double(self):
        """Return an element which is the double of the current one.

        Example:
            >>> generator = G2.get_generator()
            >>> elem = generator.double()
            >>> elem == 2 * generator
            True
        """
        res = G2Element()
        _C.g2_dbl(res.pt, self.pt)
        return res

    def idouble(self):
        """Double the current element.

        Example:
            >>> generator = G2.get_generator()
            >>> elem = G2.get_generator().idouble()
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

    @staticmethod
    def from_binary(sbin):
        """Deserialize a binary representation of the element of G2.

        Example:
            >>> generator = G2.get_generator()
            >>> bin_repr = generator.to_binary()
            >>> elem = G2Element.from_binary(bin_repr)
            >>> generator == elem
            True
        """
        elem = G2Element()
        _C.g2_read_bin(elem.pt, sbin, len(sbin))
        return elem

    def to_binary(self, compressed=True):
        """Serialize the element of G2 into a binary representation.

        Example:
            >>> generator = G2.get_generator()
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
        res = G2Element()
        _C.g2_neg(res.pt, self.pt)
        return res

    #
    # Comparison operators
    #

    def __eq__(self, other):
        """Check that the points on the EC are equal."""
        if not isinstance(other, G2Element):
            return False

        return _C.g2_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        """Check that the points on the EC are not equal."""
        if not isinstance(other, G2Element):
            return True

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

    @staticmethod
    def get_order():
        """Return the order of the EC group as a Bn large integer.

        Example:
            >>> generator = Gt.get_generator()
            >>> neutral = Gt.get_neutral_element()
            >>> order = Gt.get_order()
            >>> generator ** order == neutral
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
            >>> generator * neutral == generator
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
            >>> generator * neutral == generator
            True
        """
        neutral = GtElement()
        _C.gt_set_unity(neutral.pt)
        return neutral

    @staticmethod
    def wsum(weights, elems):
        res = Gt.get_neutral_element()
        for w, el in zip(weights, elems):
            res += w * el

        return res

    @staticmethod
    def sum(elems):
        return sum(elems)

    #
    # Aliases
    #

    get_unity = get_neutral_element
    generator = get_generator
    order = get_order


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
            >>> elem = generator ** order
            >>> elem.is_neutral_element()
            True
        """
        return bool(_C.gt_is_unity(self.pt))

    def inverse(self):
        """Return the inverse of the element of Gt."""
        res = GtElement()
        _C.gt_inv(res.pt, self.pt)
        return res

    def iinverse(self):
        """Inverse the element of Gt."""
        _C.gt_inv(self.pt, self.pt)
        return self

    def square(self):
        """Return an element which is the square of the current one.

        Example:
            >>> generator = Gt.get_generator()
            >>> elem = generator.square()
            >>> elem == generator ** 2
            True
        """
        res = GtElement()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def isquare(self):
        """Double the current element.

        Example:
            >>> generator = Gt.get_generator()
            >>> elem = Gt.get_generator().isquare()
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
        _C.gt_mul(self.pt, self.pt, other_inv.pt)
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
