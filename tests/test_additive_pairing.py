import pytest

from petrelic.additive.pairing import (
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


@pytest.fixture(params=[G1, G2, GT])
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


def test_hash_to_point_G1():
    h1 = G1.hash_to_point(b'foo')
    assert isinstance(h1, G1Element)
    h2 = G1.hash_to_point(b'bar')
    assert isinstance(h2, G1Element)
    assert h1 != h2


def test_hash_to_point_G2():
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
    assert g + g == g + g
    assert g + g == g.double()
    assert g + g == Bn(2) * g
    assert g + g == 2 * g

    assert g + g != g + g + g
    assert g + (-g) == group.neutral_element()
    d = {}
    d[2 * g] = 2
    assert d[2 * g] == 2

    # Test long names
    assert (g + g).eq(g + g)
    assert g + g == g.add(g)
    assert -g == g.neg()
    assert 10 * g == g.mul(10)

    assert len(str(g)) > 0

    neutral_element = group.neutral_element()

    assert group.infinity() == neutral_element

    assert g + neutral_element == g
    assert neutral_element + neutral_element == neutral_element


def test_g1_get_affine_coordinates():
    g = G1.generator()
    x, y = g.get_affine_coordinates()


def test_g1_export_length():
    g = G1.generator()
    assert len(g.to_binary()) == 49


def test_ec_binary_encoding(group):
    g = group.generator()
    i = group.neutral_element()

    assert g.from_binary(g.to_binary()) == g
    assert g.from_binary(i.to_binary()) == i


@pytest.mark.skip(reason="not planning to implement this for now")
def test_ec_sum(group):
    g = group.generator()
    assert group.sum([g] * 10) == (10 * g)

    order = group.order()
    h = order.random() * g
    assert group.wsum([Bn(10), Bn(20)], [g, h]) == 10 * g + 20 * h


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


def test_mul(group):
    g = group.generator()
    for _ in range(10):
        a = group.order().random()
        b = group.order().random()
        h = a * g
        k = b * g
        assert h + k == (a + b) * g


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


def test_neg(group):
    """
    Does neg negate correctly?
    """
    g = group.generator()
    a = -g
    assert -a == g

    a = g.neg()
    assert a.neg() == g


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

def test_wsum_groups(group):
    g = group.generator()

    g1 = 10 * g
    g2 = 20 * g
    a1 = Bn(2)
    a2 = Bn(4)

    s = group.wsum([g1, g2], [a1, a2])
    assert s == 100 * g

    # Make sure the type is still correct
    assert s.__class__ == g.__class__
