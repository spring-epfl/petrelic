from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other
import petrelic.constants as consts

"""
Example:
    >>> 1 == 2
    True
"""


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

    __slots__ = ["pt"]

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
        _C.g1_null(self.pt)
        _C.g1_new(self.pt)

    def __copy__(self):
        new = G1Elem()
        _C.g1_copy(new.pt, self.pt)
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
        _C.g1_sub(self.pt, self.pt, other.pt)
        return self

    def pt_double(self):
        res = G1Elem()
        _C.g1_dbl(res.pt, self.pt)
        return res

    def pt_double_inplace(self):
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
        _C.g1_neg(self.pt, self.pt)
        return self

    def __neg__(self):
        # result = copy(self)
        res = G1Elem()
        _C.g1_neg(res.pt, self.pt)
        return res

    def __ineg__(self):
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
        _C.g1_mul(self.pt, self.pt, scalar.bn)
        return self

    @force_Bn_other
    def __rmul__(self, other):
        res = G1Elem()
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

    def export(self, compressed=True):
        """ Returns a string binary representation of the point in compressed coordinates.

        Example:
            >>> from binascii import hexlify
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


def G2Group():
    pass


def G2Elem():
    pass


def GTGroup():
    pass


def GTElem():
    pass
