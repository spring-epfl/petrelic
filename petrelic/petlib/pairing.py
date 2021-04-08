r"""
This module provides a Python wrapper around RELIC's pairings using petlib's
interface: operations in :py:obj:`petrelic.native.pairings.G1` and
:py:obj:`petrelic.native.pairings.G2` are written additively, whereas operations in
:py:obj:`petrelic.native.pairings.GT` are written multiplicatively.

"""
from petrelic.bindings import _FFI, _C
from petrelic.bn import Bn, force_Bn_other
from petrelic.native.pairing import NoAffineCoordinateForECPoint

import petrelic.native.pairing as native


class BilinearGroupPair:
    """
    A bilinear group pair.

    Contains two origin groups G1, G2 and the image group GT. The underlying
    ``bplib.bp.BpGroup`` object is also embedded.
    """

    def __init__(self):
        self.GT = GTGroup()
        self.G1 = G1Group()
        self.G2 = G2Group()

    def groups(self):
        """
        Returns the three groups in the following order :  G1, G2, GT.
        """
        return self.G1, self.G2, self.GT


class G1Group(native.G1):
    """G1 group"""

    @classmethod
    def _element_type(cls):
        return G1Elem

    def check_point(self, pt):
        """Ensures the point is on the curve.

        Example:
            >>> G = G1Group()
            >>> G.check_point(G.generator())
            True
            >>> G.check_point(G.infinite())
            True
        """
        return type(pt) == self._element_type() and (pt.is_valid() or pt.is_infinite())

    @classmethod
    def infinite(cls):
        """The point at infinity.

        Alias for :py:meth:`G1.neutral_element`
        """
        return cls.neutral_element()
    # Not implemented: list_curves(), parameters(), get_points_from_x


class G1Elem(native.G1Element):
    """Element of the G1 group"""

    group = G1Group

    pt_add = native.G1Element.__add__
    pt_add_inplace = native.G1Element.__iadd__
    pt_sub = native.G1Element.__sub__
    pt_double = native.G1Element.double
    pt_double_inplace = native.G1Element.idouble
    pt_neg = native.G1Element.__neg__
    pt_neg_inplace = native.G1Element.iinverse
    pt_mul = native.G1Element.__mul__
    pt_mul_inplace = native.G1Element.__imul__
    pt_eq = native.G1Element.__eq__
    is_infinite = native.G1Element.is_neutral_element
    export = native.G1Element.to_binary
    get_affine = native.G1Element.get_affine_coordinates

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
        if not type(other) == G2Elem:
            raise TypeError("Second parameter should be of type G2Elem is {}".format(type(other)))

        res = GTElem()
        _C.pc_map(res.pt, self.pt, other.pt)
        return res


    def _get_coords(self):
        x, y, z = Bn(), Bn(), Bn()
        _C.fp_prime_back(x.bn, self.pt[0].x)
        _C.fp_prime_back(y.bn, self.pt[0].y)
        _C.fp_prime_back(z.bn, self.pt[0].z)
        return (x, y, z)


    @classmethod
    def from_binary(cls, sbin, group=None):
        return super().from_binary(sbin)


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


class G2Group(native.G2):
    """G2 group"""

    @classmethod
    def _element_type(cls):
        return G2Elem


    def check_point(self, pt):
        """Ensures the point is on the curve.

        Example:
            >>> G = G2Group()
            >>> G.check_point(G.generator())
            True
            >>> G.check_point(G.infinite())
            True
        """
        return type(pt) == self._element_type() and (pt.is_valid() or pt.is_infinite())


    @classmethod
    def infinite(cls):
        """The point at infinity.

        Alias for :py:meth:`G2.neutral_element`
        """
        return cls.neutral_element()


class G2Elem(native.G2Element):
    """Element of the G2 group"""

    group = G1Group

    pt_add = native.G2Element.__add__
    pt_add_inplace = native.G2Element.__iadd__
    pt_sub = native.G2Element.__sub__
    pt_double = native.G2Element.double
    pt_double_inplace = native.G2Element.idouble
    pt_neg = native.G2Element.__neg__
    pt_neg_inplace = native.G2Element.iinverse
    pt_mul = native.G2Element.__mul__
    pt_mul_inplace = native.G2Element.__imul__
    pt_eq = native.G2Element.__eq__
    is_infinite = native.G2Element.is_neutral_element
    export = native.G2Element.to_binary

    @classmethod
    def from_binary(cls, sbin, group=None):
        return super().from_binary(sbin)

    def __repr__(self):
        """ Representation of G2Point
        Examples:
            >>> G2Group().infinite()
            G2Elem(00)
            >>> G2Group().generator()
            G2Elem(02024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb813e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e)
        """
        pt_hex = self.to_binary().hex()
        return "G2Elem({})".format(pt_hex)


class GTGroup(native.GT):
    """GT group"""

    @classmethod
    def _element_type(cls):
        return GTElem

    def check_elem(self, pt):
        """Ensures the element is an element of the group

        Example:
            >>> G = GTGroup()
            >>> G.check_elem(G.generator())
            True
            >>> G.check_elem(G.unity())
            True
        """

        return type(pt) == self._element_type() and pt.is_valid()

    # Not implemented: list_curves(), parameters(), get_points_from_x


class GTElem(native.GTElement):
    """GT element"""

    group = GTGroup

    mul_inplace = native.GTElement.__imul__
    inv = native.GTElement.inverse
    inv_inplace = native.GTElement.iinverse
    sqr = native.GTElement.square
    sqr_inplace = native.GTElement.isquare
    exp = native.GTElement.__pow__
    exp_inplace = native.GTElement.__ipow__
    export = native.GTElement.to_binary

    @classmethod
    def from_binary(cls, sbin, group=None):
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

        return super().from_binary(sbin)


    def __repr__(self):
        """ Representation of GTPoint
        Examples:
            >>> GTGroup().generator()
            GTElem(1368bb445c7c2d209703f239689ce34c0378a68e72a6b3b216da0e22a5031b54ddff57309396b38c881c4c849ec23e87193502b86edb8857c273fa075a50512937e0794e1e65a7617c90d8bd66065b1fffe51d7a579973b1315021ec3c19934f01b2f522473d171391125ba84dc4007cfbf2f8da752f7c74185203fcca589ac719c34dffbbaad8431dad1c1fb597aaa5018107154f25a764bd3c79937a45b84546da634b8f6be14a8061e55cceba478b23f7dacaa35c8ca78beae9624045b4b619f26337d205fb469cd6bd15c3d5a04dc88784fbb3d0b2dbdea54d43b2b73f2cbb12d58386a8703e0f948226e47ee89d06fba23eb7c5af0d9f80940ca771b6ffd5857baaf222eb95a7d2809d61bfe02e1bfd1b68ff02f0b8102ae1c2d5d5ab1a04c581234d086a9902249b64728ffd21a189e87935a954051c7cdba7b3872629a4fafc05066245cb9108f0242d0fe3ef0f41e58663bf08cf068672cbd01a7ec73baca4d72ca93544deff686bfd6df543d48eaa24afe47e1efde449383b676631)
        """
        pt_hex = self.to_binary().hex()
        return "GTElem({})".format(pt_hex)
