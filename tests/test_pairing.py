import copy

from petrelic.native.pairing import (
    BilinearGroupPair,
    G1,
    G1Element,
    G2,
    G2Element,
    GT,
    GTElement,
    NoAffineCoordinateForECPoint
)
from petrelic.bn import Bn

import pytest


@pytest.fixture(params=[G1, G2])
def group(request):
    return request.param

@pytest.fixture(params=[G1Element, G2Element])
def element(request):
    return request.param


def test_bgp():
    bgp = BilinearGroupPair()
    groups = bgp.groups()

    assert isinstance(groups[0], G1)
    assert isinstance(groups[1], G2)
    assert isinstance(groups[2], GT)


def test_is_valid(group):
    assert group.generator().is_valid()
    assert (100 * group.generator()).is_valid()


def test_is_valid_gt():
    assert GT.unity().is_valid()
    assert GT.generator().is_valid()
    assert (GT.generator() ** 100).is_valid()

def test_copy(group):
    elem = 42 * group.generator()
    elem_copy = copy.copy(elem)

    assert elem == elem_copy

    elem += group.generator()
    assert elem != elem_copy


def test_copy_gt():
    elem = GT.generator() ** 42
    elem_copy = copy.copy(elem)

    assert elem == elem_copy

    elem *= GT.generator()
    assert elem != elem_copy


def test_hash_to_point_G1(group):
    h1 = G1.hash_to_point(b'foo')
    assert isinstance(h1, G1Element)
    h2 = G1.hash_to_point(b'bar')
    assert isinstance(h2, G1Element)
    assert h1 != h2


def test_hash_to_point_G2(group):
    h1 = G2.hash_to_point(b'foo')
    assert isinstance(h1, G2Element)
    h2 = G2.hash_to_point(b'bar')
    assert isinstance(h2, G2Element)
    assert h1 != h2


@pytest.mark.skip(reason="not planning to implement this for now")
def test_ec_from_x(group):
    g = group.generator()
    x, y = g.get_affine_coordinates()

    g1, g2 = group.get_points_from_x(x)
    assert g == g1 or g == g2


def test_ec_arithmetic(group):
    g = group.generator()
    assert not g == 5
    assert g != 5
    assert g + g == g + g
    assert g + g == g.double()
    assert g + g == Bn(2) * g
    assert g + g == 2 * g

    assert g + g != g + g + g
    assert g + (-g) == group.neutral_element()
    d = {}
    d[2 * g] = 2
    assert d[2 * g] == 2

    q = group.generator()
    q *= 10

    assert q == g * 10

    q *= 10
    assert q == g * 10 * 10

    # Test long names
    assert (g + g).eq(g + g)
    assert g + g == g.add(g)
    assert -g == g.neg()
    assert 10 * g == g.mul(10)

    assert len(str(g)) > 0


def test_gt_multiplication():
    g = GT.generator()
    assert not g == 5
    assert g != 5
    assert g * g == g * g
    assert g * g == g.square()
    assert g * g == g ** Bn(2)
    assert g * g == g ** 2
    assert g * g * g == g ** 3

    assert g * g != g * g * g


def test_gt_neutral_element():
    g = GT.generator()
    neutral_element = GT.neutral_element()

    assert g * neutral_element == g
    assert neutral_element * neutral_element == neutral_element


def test_gt_inverse():
    g = GT.generator()
    elem = g ** 1337

    assert elem * elem.inverse() == GT.neutral_element()
    assert elem.inverse() == elem ** (-1)


def test_gt_exponentiation():
    g = GT.generator()

    assert g ** 3 == g * g * g
    assert g ** (-1) == g.inverse()
    assert g ** 10 == g.pow(10)
    assert g ** Bn(10) == g.pow(Bn(10))


def test_g1_get_affine_coordinates():
    g = G1.generator()
    x, y = g.get_affine_coordinates()


def test_g1_export_length():
    g = G1.generator()
    assert len(g.to_binary()) == 49


def test_ec_binary_encoding(group):
    g = group.generator()
    i = group.neutral_element()

    assert len(i.to_binary()) == 1
    assert g.from_binary(g.to_binary()) == g
    assert g.from_binary(i.to_binary()) == i


def test_gt_binary_encoding(group):
    g = GT.generator()
    i = GT.neutral_element()

    assert GTElement.from_binary(g.to_binary()) == g
    assert GTElement.from_binary(i.to_binary()) == i


@pytest.mark.skip(reason="not planning to implement this for now")
def test_ec_sum(group):
    g = group.generator()
    assert group.sum([g] * 10) == (10 * g)

    order = group.order()
    h = order.random() * g
    assert group.wsum([Bn(10), Bn(20)], [g, h]) == 10 * g + 20 * h


@pytest.mark.skip(reason="not planning to implement this for now")
def test_gt_prod():
    g = GT.generator()
    assert group.prod([g] * 10) == (g ** 10)

    order = GT.order()
    h = g ** order.random()
    assert group.wprod([Bn(10), Bn(20)], [g, h]) == g ** 10 * h ** 20


def test_iadd(group):
    """
    Does pt_add_inplace add correctly?
    """
    g = group.generator()
    a = g + g
    g += g
    assert a == g

    # Does it save the result in the same memory location?

    a = group.generator()
    b = a
    a += a
    assert id(b) == id(a)


def test_imul():
    g = GT.generator()
    a = g * g
    b = GT.generator()
    b *= g
    assert a == b


def test_double(group):
    """
    Does double() double correctly?
    """
    g = group.generator()
    a = g.double()
    g.idouble()
    assert a == g

    # Does it save the result in the same memory location?
    a = group.generator()
    b = a
    a.idouble()
    assert id(b) == id(a)


def test_square():
    """
    Does square() square correctly?
    """
    g = GT.generator()
    a = g.square()
    b = GT.generator()
    b.isquare()
    assert a == b

    # Does it save the result in the same memory location?

    a = GT.generator()
    b = a
    a.isquare()
    assert id(b) == id(a)


def test_imul(group):
    """
    Does imul multiply correctly?
    """
    g = group.generator()
    a = g.mul(5)
    g *= 5
    assert a == g

    # Does it save the result in the same memory location?

    a = group.generator()
    b = a
    a *= 5
    assert id(b) == id(a)


def test_iexp():
    g = GT.generator()
    a = g ** 100
    g **= 100
    assert a == g

    a = GT.generator()
    b = a
    a **= 10
    assert id(b) == id(a)


def test_neg(group):
    """
    Does neg negate correctly?
    """
    g = group.generator()
    a = -g
    assert -a == g

    a = g.neg()
    assert a.neg() == g


def test_inverse():
    g = GT.generator()
    a = g.inverse()
    g.iinverse()
    assert a == g

    a = GT.generator()
    b = a
    a.iinverse()
    assert id(b) == id(a)


def test_g1_affine_inf():
    group = G1()
    inf = group.neutral_element()

    with pytest.raises(NoAffineCoordinateForECPoint) as ex:
        inf.get_affine_coordinates()


def test_ec_bin_translation(group):
    from timeit import default_timer as timer

    o = group.order()
    g = group.generator()
    pt1000 = [o.random() * g for _ in range(1000)]

    exp = []
    for pt in pt1000:
        exp += [pt.to_binary()]

    # Unprecise time estimation

    t0 = timer()
    for ept in exp:
        g.from_binary(ept)
    t1 = timer()
    print("\nParsed compressed Pt: %2.4f" % (t1 - t0))

    exp = []
    for pt in pt1000:
        exp += [pt.to_binary(compressed=False)]

    t0 = timer()
    for ept in exp:
        g.from_binary(ept)
    t1 = timer()
    print("\nParsed uncompressed Pt: %2.4f" % (t1 - t0))


def test_gt_bin_translation():
    g = GT.generator()
    o = GT.order()

    a = o.random()
    elem = g ** a

    # Test compresed
    binary = elem.to_binary()
    assert g.from_binary(binary) == elem

    # Test non-compressedj
    binary = elem.to_binary(compressed=False)
    assert g.from_binary(binary) == elem

