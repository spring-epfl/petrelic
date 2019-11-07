"""Petlib compatible API of the petrelic library.
"""
from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other
import petrelic.constants as consts

from binascii import hexlify


class BilinearGroupPair:
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group GT. The underlying
    ``bplib.bp.BpGroup`` object is also embedded.
    """

    def __init__(self):
        self.GT = GTGroup(self)
        self.G1 = G1Group(self)
        self.G2 = G2Group(self)

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, GT.
        """
        return self.G1, self.G2, self.GT


class G1Group:
    def __init__(self):
        pass

    def generator(self):
        """Returns the generator of the EC group."""

        pt = G1Elem()
        _C.g1_get_gen(pt.pt)
        pt._is_gen = True
        return pt

    def infinite(self):
        """Returns a point at infinity.

        Example:
            >>> G = G1Group()
            >>> G.generator() + G.infinite() == G.generator() ## Should hold.
            True
        """
        pt = G1Elem()
        _C.g1_set_infty(pt.pt)
        return pt

    def order(self):
        """Returns the order of the group as a Big Number.

        Example:
            >>> G = G1Group()
            >>> G.order() * G.generator() == G.infinite() ## Should hold.
            True
        """

        ord = Bn()
        _C.g1_get_ord(ord.bn)
        return ord

    def check_point(self, pt):
        """Ensures the point is on the curve.

        Example:
            >>> G = G1Group()
            >>> G.check_point(G.generator())
            True
            >>> G.check_point(G.infinite())
            True
        """
        return bool(_C.g1_is_valid(pt.pt))

    def sum(self, elems):
        """Sums a number of elements (not optimized)"""

        res = G1Group().infinite()
        for el in elems:
            res += el

        return res

    def wsum(self, weights, elems):
        """Sums a number of elements (not optimized)"""

        # TODO: can be optimized a little by doing groups of 2
        res = G1Group().infinite()
        for w, el in zip(weights, elems):
            res += w * el

        return res

    def hash_to_point(self, hinput):
        """Hash a byte string into an EC Point."""
        res = G1Elem()
        _C.g1_map(res.pt, hinput, len(hinput))

    # Not implemented: list_curves(), parameters(), get_points_from_x


class G1Elem:

    __slots__ = ["pt", "_is_gen"]

    @staticmethod
    def from_binary(sbin, group=None):
        """Create a point from a byte sequence.

        It accepts (but ignores) group as extra argument.

        Example:
            >>> G = G1Group()
            >>> byte_string = G.generator().export()                # Export EC point as byte string
            >>> G1Elem.from_binary(byte_string, G) == G.generator()    # Import EC point from binary string
            True
            >>> G1Elem.from_binary(byte_string, G) == G.generator()    # Import EC point from binary string
            True
        """

        ret = G1Elem()
        _C.g1_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def __init__(self):
        """Initialize a new g1 element"""
        self.pt = _FFI.new("g1_t")
        self._is_gen = False
        _C.g1_null(self.pt)
        _C.g1_new(self.pt)

    def __copy__(self):
        new = G1Elem()
        _C.g1_copy(new.pt, self.pt)
        new._is_gen = self._is_gen
        return new

    def pt_add(self, other):
        """Adds two points together. Synonym with self + other.

        Example:
            >>> g = G1Group().generator()
            >>> g.pt_add(g) == (g + g) == (2 * g) == g.pt_double() # Equivalent formulations
            True
        """
        return self.__add__(other)

    def pt_add_inplace(self, other):
        """Adds two points together and puts the result in self.pt.
        """
        return self.__iadd__(other)

    def __add__(self, other):
        res = G1Elem()
        _C.g1_add(res.pt, self.pt, other.pt)
        return res

    def __iadd__(self, other):
        self._is_gen = False
        _C.g1_add(self.pt, self.pt, other.pt)
        return self

    def pt_sub(self, other):
        """Subtract two points. Synonym with self - other.

        Example:
            >>> g = G1Group().generator()
            >>> g.pt_sub(g) == G1Group().infinite()
            True
        """
        return self.__sub__(other)

    def __sub__(self, other):
        res = G1Elem()
        _C.g1_sub(res.pt, self.pt, other.pt)
        return res

    def __isub__(self, other):
        self._is_gen = False
        _C.g1_sub(self.pt, self.pt, other.pt)
        return self

    def pt_double(self):
        res = G1Elem()
        _C.g1_dbl(res.pt, self.pt)
        return res

    def pt_double_inplace(self):
        self._is_gen = False
        _C.g1_dbl(self.pt, self.pt)
        return self

    def pt_neg(self):
        """Returns the negative of the point. Synonym with -self.

        Example:
            >>> G = G1Group()
            >>> g = G.generator()
            >>> g + (-g) == G.infinite() # Unary negative operator.
            True
            >>> g - g == G.infinite()    # Binary negative operator.
            True
        """

        return self.__neg__()

    def pt_neg_inplace(self):
        # result = copy(self)
        return self.__ineg__()

    def __neg__(self):
        # result = copy(self)
        res = G1Elem()
        _C.g1_neg(res.pt, self.pt)
        return res

    def __ineg__(self):
        self._is_gen = False
        _C.g1_neg(self.pt, self.pt)
        return self

    def pt_mul(self, scalar):
        """Returns the product of the point with a scalar (not commutative). Synonym with scalar * self.

        Example:
            >>> G = G1Group()
            >>> g = G.generator()
            >>> 100 * g == g.pt_mul(100) # Operator and function notation mean the same
            True
            >>> G.order() * g == G.infinite() # Scalar mul. by the order returns the identity element.
            True
        """
        return self.__rmul__(scalar)

    @force_Bn_other
    def pt_mul_inplace(self, scalar):
        """ Multiplies a scalar with a point and mutates the point to hold the result.
        """
        self._is_gen = False
        _C.g1_mul(self.pt, self.pt, scalar.bn)
        return self

    @force_Bn_other
    def __rmul__(self, other):
        res = G1Elem()
        if self._is_gen:
            _C.g1_mul_gen(res.pt, other.bn)
        else:
            _C.g1_mul(res.pt, self.pt, other.bn)
        return res

    def pt_eq(self, other):
        """Returns a boolean denoting whether the points are equal. Synonym with self == other.

        Example:
            >>> G = G1Group()
            >>> g = G.generator()
            >>> 40 * g + 60 * g == 100 * g
            True
            >>> g == 2 * g
            False
        """
        return self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, G1Elem):
            return False

        return _C.g1_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_infinite(self):
        """Returns True if this point is at infinity, otherwise False.

        Example:
            >>> G = G1Group()
            >>> g, o = G.generator(), G.order()
            >>> (o * g).is_infinite()
            True
            >>> G.infinite().is_infinite()
            True
        """
        _C.g1_norm(self.pt, self.pt)
        return bool(_C.g1_is_infty(self.pt))

    def pair(self, other):
        """Computes bilinear pairing with self and otherwise

        Examples:
            >>> G1 = G1Group()
            >>> G2 = G2Group()
            >>> GT = GTGroup()
            >>> G1.generator().pair(G2.generator()) == GT.generator()
            True

            >>> p = 100 * G1.generator()
            >>> q = 200 * G2.generator()
            >>> p.pair(q) == GT.generator() ** 20000
            True
        """
        res = GTElem()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res

    def export(self, compressed=True):
        """ Returns a string binary representation of the point in compressed coordinates.

        Example:
            >>> G = G1Group()
            >>> pt = 10 * G.generator()
            >>> byte_string = pt.export()
            >>> G1Elem.from_binary(byte_string) == pt
            True
        """
        flag = int(compressed)
        length = _C.g1_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.g1_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    def _get_coords(self):
        x, y, z = Bn(), Bn(), Bn()
        _C.fp_prime_back(x.bn, self.pt[0].x)
        _C.fp_prime_back(y.bn, self.pt[0].y)
        _C.fp_prime_back(z.bn, self.pt[0].z)
        return (x, y, z)

    def __hash__(self):
        return self.export().__hash__()

    def get_affine(self):
        """Return the affine coordinates (x,y) of this EC Point.

        Example:
            >>> G = G1Group()
            >>> g = G.generator()
            >>> x, y = g.get_affine()
            >>> x
            Bn(3685416753713387016781088315183077757961620795782546409894578378688607592378376318836054947676345821548104185464507)
            >>> y
            Bn(1339506544944476473020471379941921221584933875938349620426543736416511423956333506472724655353366534992391756441569)
        """
        if self.is_infinite():
            raise Exception("EC Infinity has no affine coordinates.")

        x, y, _ = self._get_coords()
        return (x, y)

    def __repr__(self):
        """ Representation of G1Point

        Examples:
            >>> G1Group().infinite()
            G1Elem(0, 0, 0)
            >>> G1Group().generator()
            G1Elem(3685416753713387016781088315183077757961620795782546409894578378688607592378376318836054947676345821548104185464507, 1339506544944476473020471379941921221584933875938349620426543736416511423956333506472724655353366534992391756441569, 1)
        """
        x, y, z = self._get_coords()
        return "G1Elem({}, {}, {})".format(x, y, z)


class G2Group:
    def __init__(self):
        pass

    def generator(self):
        """Returns the generator of the EC group."""

        pt = G2Elem()
        _C.g2_get_gen(pt.pt)
        return pt

    def infinite(self):
        """Returns a point at infinity.

        Example:
            >>> G = G2Group()
            >>> G.generator() + G.infinite() == G.generator() ## Should hold.
            True
        """
        pt = G2Elem()
        _C.g2_set_infty(pt.pt)
        return pt

    def order(self):
        """Returns the order of the group as a Big Number.

        Example:
            >>> G = G2Group()
            >>> G.order() * G.generator() == G.infinite() ## Should hold.
            True
        """

        ord = Bn()
        _C.g2_get_ord(ord.bn)
        return ord

    def check_point(self, pt):
        """Ensures the point is on the curve.

        Example:
            >>> G = G2Group()
            >>> G.check_point(G.generator())
            True
            >>> G.check_point(G.infinite())
            True
        """
        return bool(_C.g2_is_valid(pt.pt))

    def sum(self, elems):
        """Sums a number of elements (not optimized)"""

        res = G2Group().infinite()
        for el in elems:
            res += el

        return res

    def wsum(self, weights, elems):
        """Sums a number of elements (not optimized)"""

        # TODO: can be optimized a little by doing groups of 2
        res = G2Group().infinite()
        for w, el in zip(weights, elems):
            res += w * el

        return res

    def hash_to_point(self, hinput):
        """Hash a byte string into an EC Point."""
        res = G2Elem()
        _C.g2_map(res.pt, hinput, len(hinput))

    # Not implemented: list_curves(), parameters(), get_points_from_x


class G2Elem:

    __slots__ = ["pt"]

    @staticmethod
    def from_binary(sbin, group=None):
        """Create a point from a byte sequence.

        It accepts (but ignores) group as extra argument.

        Example:
            >>> G = G2Group()
            >>> byte_string = G.generator().export()                # Export EC point as byte string
            >>> G2Elem.from_binary(byte_string, G) == G.generator()    # Import EC point from binary string
            True
            >>> G2Elem.from_binary(byte_string, G) == G.generator()    # Import EC point from binary string
            True
        """

        ret = G2Elem()
        _C.g2_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def __init__(self):
        """Initialize a new g1 element"""
        self.pt = _FFI.new("g2_t")
        _C.g2_null(self.pt)
        _C.g2_new(self.pt)

    def __copy__(self):
        new = G2Elem()
        _C.g2_copy(new.pt, self.pt)
        return new

    def pt_add(self, other):
        """Adds two points together. Synonym with self + other.

        Example:
            >>> g = G2Group().generator()
            >>> g.pt_add(g) == (g + g) == (2 * g) == g.pt_double() # Equivalent formulations
            True
        """
        return self.__add__(other)

    def pt_add_inplace(self, other):
        """Adds two points together and puts the result in self.pt.
        """
        return self.__iadd__(other)

    def __add__(self, other):
        res = G2Elem()
        _C.g2_add(res.pt, self.pt, other.pt)
        return res

    def __iadd__(self, other):
        _C.g2_add(self.pt, self.pt, other.pt)
        return self

    def pt_sub(self, other):
        """Subtract two points. Synonym with self - other.

        Example:
            >>> g = G2Group().generator()
            >>> g.pt_sub(g) == G2Group().infinite()
            True
        """
        return self.__sub__(other)

    def __sub__(self, other):
        res = G2Elem()
        _C.g2_sub(res.pt, self.pt, other.pt)
        return res

    def __isub__(self, other):
        _C.g2_sub(self.pt, self.pt, other.pt)
        return self

    def pt_double(self):
        res = G2Elem()
        _C.g2_dbl(res.pt, self.pt)
        return res

    def pt_double_inplace(self):
        _C.g2_dbl(self.pt, self.pt)
        return self

    def pt_neg(self):
        """Returns the negative of the point. Synonym with -self.

        Example:
            >>> G = G2Group()
            >>> g = G.generator()
            >>> g + (-g) == G.infinite() # Unary negative operator.
            True
            >>> g - g == G.infinite()    # Binary negative operator.
            True
        """

        return self.__neg__()

    def pt_neg_inplace(self):
        # result = copy(self)
        _C.g2_neg(self.pt, self.pt)
        return self

    def __neg__(self):
        # result = copy(self)
        res = G2Elem()
        _C.g2_neg(res.pt, self.pt)
        return res

    def __ineg__(self):
        _C.g2_neg(self.pt, self.pt)
        return self

    def pt_mul(self, scalar):
        """Returns the product of the point with a scalar (not commutative). Synonym with scalar * self.

        Example:
            >>> G = G2Group()
            >>> g = G.generator()
            >>> 100 * g == g.pt_mul(100) # Operator and function notation mean the same
            True
            >>> G.order() * g == G.infinite() # Scalar mul. by the order returns the identity element.
            True
        """
        return self.__rmul__(scalar)

    @force_Bn_other
    def pt_mul_inplace(self, scalar):
        """ Multiplies a scalar with a point and mutates the point to hold the result.
        """
        _C.g2_mul(self.pt, self.pt, scalar.bn)
        return self

    @force_Bn_other
    def __rmul__(self, other):
        res = G2Elem()
        _C.g2_mul(res.pt, self.pt, other.bn)
        return res

    def pt_eq(self, other):
        """Returns a boolean denoting whether the points are equal. Synonym with self == other.

        Example:
            >>> G = G2Group()
            >>> g = G.generator()
            >>> 40 * g + 60 * g == 100 * g
            True
            >>> g == 2 * g
            False
        """
        return self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, G2Elem):
            return False

        return _C.g2_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_infinite(self):
        """Returns True if this point is at infinity, otherwise False.

        Example:
            >>> G = G2Group()
            >>> g, o = G.generator(), G.order()
            >>> (o * g).is_infinite()
            True
            >>> G.infinite().is_infinite()
            True
        """
        _C.g2_norm(self.pt, self.pt)
        return bool(_C.g2_is_infty(self.pt))

    def export(self, compressed=True):
        """ Returns a string binary representation of the point in compressed coordinates.

        Example:
            >>> G = G2Group()
            >>> pt = 10 * G.generator()
            >>> byte_string = pt.export()
            >>> G2Elem.from_binary(byte_string) == pt
            True
        """
        flag = int(compressed)
        length = _C.g2_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.g2_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    def __hash__(self):
        return self.export().__hash__()

    def __repr__(self):
        """ Representation of G2Point

        Examples:
            >>> G2Group().infinite()
            G2Elem(00)
            >>> G2Group().generator()
            G2Elem(02024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb813e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e)
        """
        hx = hexlify(self.export()).decode("utf-8")
        return "G2Elem({})".format(hx)


class GTGroup:
    def __init__(self):
        pass

    def generator(self):
        """Returns the generator of the group."""

        pt = GTElem()
        _C.gt_get_gen(pt.pt)
        return pt

    def unity(self):
        """Returns the unity element

        Example:
            >>> G = GTGroup()
            >>> G.generator() * G.unity() == G.generator() ## Should hold.
            True
        """
        pt = GTElem()
        _C.gt_set_unity(pt.pt)
        return pt

    def order(self):
        """Returns the order of the group as a Big Number.

        Example:
            >>> G = GTGroup()
            >>> G.generator() ** G.order() == G.unity() ## Should hold.
            True
        """

        ord = Bn()
        _C.gt_get_ord(ord.bn)
        return ord

    # TODO: was check_point
    def check_elem(self, pt):
        """Ensures the element is an element of the group

        Example:
            >>> G = GTGroup()
            >>> G.check_elem(G.generator())
            True
            >>> G.check_elem(G.unity())
            True
        """
        # TODO: for some reason gt_is_valid doesn't accept unity
        if pt == self.unity():
            return True

        return bool(_C.gt_is_valid(pt.pt))

    def prod(self, elems):
        """Product of a number of elements (not optimized)"""

        res = GTGroup().unity()
        for el in elems:
            res *= el

        return res

    def wprod(self, weights, elems):
        """Weighted product of a number of elements (not optimized)"""

        # TODO: can be optimized a little by doing groups of 2
        res = GTGroup().unity()
        for w, el in zip(weights, elems):
            res *= el ** w

        return res

    # Not implemented: list_curves(), parameters(), get_points_from_x


class GTElem:

    __slots__ = ["pt"]

    @staticmethod
    def from_binary(sbin, group=None):
        """Create an element from a byte sequence.

        It accepts (but ignores) group as extra argument.

        Example:
            >>> G = GTGroup()
            >>> byte_string = G.generator().export()                # Export EC point as byte string
            >>> GTElem.from_binary(byte_string, G) == G.generator()    # Import EC point from binary string
            True
            >>> GTElem.from_binary(byte_string) == G.generator()    # Import EC point from binary string
            True
        """

        ret = GTElem()
        _C.gt_read_bin(ret.pt, sbin, len(sbin))
        return ret

    def __init__(self):
        """Initialize a new g1 element"""
        self.pt = _FFI.new("gt_t")
        _C.gt_null(self.pt)
        _C.gt_new(self.pt)

    def __copy__(self):
        new = GTElem()
        _C.gt_copy(new.pt, self.pt)
        return new

    def mul(self, other):
        """Multiplies two elements together. Synonym with self * other.

        Example:
            >>> g = GTGroup().generator()
            >>> g.mul(g) == (g * g) == (g ** 2) == g.sqr() # Equivalent formulations
            True
        """
        return self.__mul__(other)

    def mul_inplace(self, other):
        """Adds two points together and puts the result in self.pt.
        """
        return self.__imul__(other)

    def __mul__(self, other):
        res = GTElem()
        _C.gt_mul(res.pt, self.pt, other.pt)
        return res

    def __imul__(self, other):
        _C.gt_mul(self.pt, self.pt, other.pt)
        return self

    def div(self, other):
        """Subtract two points. Synonym with self - other.

        Example:
            >>> g = GTGroup().generator()
            >>> g.div(g) == GTGroup().unity()
            True
        """
        return self.__truediv__(other)

    def __truediv__(self, other):
        res = other.inv()
        _C.gt_mul(res.pt, self.pt, res.pt)
        return res

    def __itruediv__(self, other):
        otherinv = other.inv()
        _C.gt_mul(self.pt, self.pt, otherinv.pt)
        return self

    def __floordiv__(self, other):
        return self.__truediv__(other)

    def __ifloordiv__(self, other):
        return self.__itruediv__(other)

    def inv(self):
        """Returns the inverse of the element. Synonym with self ** -1.

        Example:
            >>> G = GTGroup()
            >>> g = G.generator()
            >>> g * g.inv() == G.unity()    # Inversion function
            True
            >>> g * (g ** -1) == G.unity()    # Unary negative operator.
            True
            >>> g / g == G.unity()          # Binary operator
            True
        """
        res = GTElem()
        _C.gt_inv(res.pt, self.pt)
        return res

    def inv_inplace(self):
        """Inverts the elements, and puts the result in self"""
        _C.gt_inv(self.pt, self.pt)
        return self

    def sqr(self):
        """Squares the element

        Example:
            >>> g = GTGroup().generator()
            >>> g.sqr() == g * g
            True
        """
        res = GTElem()
        _C.gt_sqr(res.pt, self.pt)
        return res

    def sqr_inplace(self):
        """Squares the element, and puts the result in self"""
        _C.gt_sqr(self.pt, self.pt)
        return self

    def exp(self, scalar):
        """Exponentiates the element with a scalar. Synonym with self ** scalar.

        Example:
            >>> G = GTGroup()
            >>> g = G.generator()
            >>> g ** 100 == g.exp(100) # Operator and function notation mean the same
            True
            >>> g ** G.order () == G.unity() # Scalar mul. by the order returns the identity element.
            True
        """
        return self.__pow__(scalar)

    def exp_inplace(self, scalar):
        """ Exponentiates the element with a scalar and mutates the element to hold the result.
        """
        return self.__ipow__(scalar)

    @force_Bn_other
    def __pow__(self, other):
        res = GTElem()
        exp = other.mod(GTGroup().order())
        _C.gt_exp(res.pt, self.pt, exp.bn)
        return res

    @force_Bn_other
    def __ipow__(self, other):
        _C.gt_exp(self.pt, self.pt, other.bn)
        return self

    def eq(self, other):
        """Returns a boolean denoting whether the points are equal. Synonym with self == other.

        Example:
            >>> G = GTGroup()
            >>> g = G.generator()
            >>> (g ** 40) * (g ** 60) == g ** 100
            True
            >>> g == g ** 2
            False
        """
        return self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, GTElem):
            return False

        return _C.gt_cmp(self.pt, other.pt) == _C.CONST_RLC_EQ

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_unity(self):
        """Returns True if this element is the unity element, otherwise False.

        Example:
            >>> G = GTGroup()
            >>> g, o = G.generator(), G.order()
            >>> (g ** o).is_unity()
            True
            >>> G.unity().is_unity()
            True
            >>> g.is_unity()
            False
        """
        return bool(_C.gt_is_unity(self.pt))

    def export(self, compressed=True):
        """ Returns a string binary representation of the point in compressed coordinates.

        Example:
            >>> G = GTGroup()
            >>> pt = G.generator() ** 10
            >>> byte_string = pt.export()
            >>> GTElem.from_binary(byte_string) == pt
            True
        """
        flag = int(compressed)
        length = _C.gt_size_bin(self.pt, flag)
        buf = _FFI.new("char[]", length)
        _C.gt_write_bin(buf, length, self.pt, flag)
        return _FFI.unpack(buf, length)

    def __hash__(self):
        return self.export().__hash__()

    def __repr__(self):
        """ Representation of GTPoint

        Examples:
            >>> GTGroup().generator()
            GTElem(1368bb445c7c2d209703f239689ce34c0378a68e72a6b3b216da0e22a5031b54ddff57309396b38c881c4c849ec23e87193502b86edb8857c273fa075a50512937e0794e1e65a7617c90d8bd66065b1fffe51d7a579973b1315021ec3c19934f01b2f522473d171391125ba84dc4007cfbf2f8da752f7c74185203fcca589ac719c34dffbbaad8431dad1c1fb597aaa5018107154f25a764bd3c79937a45b84546da634b8f6be14a8061e55cceba478b23f7dacaa35c8ca78beae9624045b4b619f26337d205fb469cd6bd15c3d5a04dc88784fbb3d0b2dbdea54d43b2b73f2cbb12d58386a8703e0f948226e47ee89d06fba23eb7c5af0d9f80940ca771b6ffd5857baaf222eb95a7d2809d61bfe02e1bfd1b68ff02f0b8102ae1c2d5d5ab1a04c581234d086a9902249b64728ffd21a189e87935a954051c7cdba7b3872629a4fafc05066245cb9108f0242d0fe3ef0f41e58663bf08cf068672cbd01a7ec73baca4d72ca93544deff686bfd6df543d48eaa24afe47e1efde449383b676631)
        """
        hx = hexlify(self.export()).decode("utf-8")
        return "GTElem({})".format(hx)
