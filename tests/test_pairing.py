from petrelic.pairing import G1, G1Element, G2, G2Element, Gt, GtElement, NoAffineCoordinateForECPoint
from petrelic.bn import Bn

import pytest


@pytest.fixture(params=[G1, G2])
def group(request):
    return request.param

@pytest.fixture(params=[G1Element, G2Element])
def element(request):
    return request.param

def test_is_valid(group):
    assert group.get_generator().is_valid()
    assert (100 * group.get_generator()).is_valid()


def test_is_valid_gt():
    assert Gt.get_generator().is_valid()
    assert (Gt.get_generator() ** 100).is_valid()


def test_from_hashed_bytes(element):
    h1 = element.from_hashed_bytes(b'foo')
    assert(isinstance(h1, element))
    h2 = element.from_hashed_bytes(b'bar')
    assert(isinstance(h2, element))
    assert(h1 != h2)


@pytest.mark.skip(reason="not planning to implement this for now")
def test_ec_from_x(group):
    g = group.get_generator()
    x, y = g.get_affine_coordinates()

    g1, g2 = group.get_points_from_x(x)
    assert g == g1 or g == g2


def test_ec_arithmetic(group):
    g = group.get_generator()
    assert g + g == g + g
    assert g + g == g.get_double()
    assert g + g == Bn(2) * g
    assert g + g == 2 * g

    assert g + g != g + g + g
    assert g + (-g) == group.get_neutral_element()
    d = {}
    d[2 * g] = 2
    assert d[2 * g] == 2

    # Test long names
    assert (g + g).eq(g + g)
    assert g + g == g.add(g)
    assert -g == g.neg()
    assert 10 * g == g.mul(10)

    assert len(str(g)) > 0


def test_gt_multiplication():
    g = Gt.get_generator()
    assert g * g == g * g
    assert g * g == g.get_square()
    assert g * g == g ** Bn(2)
    assert g * g == g ** 2
    assert g * g * g == g ** 3

    assert g * g != g * g * g


def test_gt_neutral_element():
    g = Gt.get_generator()
    neutral_element = Gt.get_neutral_element()

    assert g * neutral_element == g
    assert neutral_element * neutral_element == neutral_element


def test_gt_inverse():
    g = Gt.get_generator()
    elem = g ** 1337

    assert elem * elem.get_inverse() == Gt.get_neutral_element()
    assert elem.get_inverse() == elem ** (-1)


def test_gt_exponentiation():
    g = Gt.get_generator()

    assert g ** 3 == g * g * g
    assert g ** (-1) == g.get_inverse()
    assert g ** 10 == g.pow(10)
    assert g ** Bn(10) == g.pow(Bn(10))


def test_g1_get_affine_coordinates():
    g = G1.get_generator()
    x, y = g.get_affine_coordinates()


def test_g1_export_length():
    g = G1.get_generator()
    assert len(g.to_binary()) == 49


def test_ec_binary_encoding(group):
    g = group.get_generator()
    i = group.get_neutral_element()

    assert len(i.to_binary()) == 1
    assert g.from_binary(g.to_binary()) == g
    assert g.from_binary(i.to_binary()) == i


def test_gt_binary_encoding(group):
    g = Gt.get_generator()
    i = Gt.get_neutral_element()

    assert GtElement.from_binary(g.to_binary()) == g
    assert GtElement.from_binary(i.to_binary()) == i


@pytest.mark.skip(reason="not planning to implement this for now")
def test_ec_sum(group):
    g = group.get_generator()
    assert group.sum([g] * 10) == (10 * g)

    order = group.get_order()
    h = order.random() * g
    assert group.wsum([Bn(10), Bn(20)], [g, h]) == 10 * g + 20 * h


@pytest.mark.skip(reason="not planning to implement this for now")
def test_gt_prod():
    g = Gt.get_generator()
    assert group.prod([g] * 10) == (g ** 10)

    order = Gt.get_order()
    h = g ** order.random()
    assert group.wprod([Bn(10), Bn(20)], [g, h]) == g ** 10 * h ** 20


def test_iadd(group):
    """
    Does pt_add_inplace add correctly?
    """
    g = group.get_generator()
    a = g + g
    g += g
    assert a == g

    # Does it save the result in the same memory location?

    a = group.get_generator()
    b = a
    a += a
    assert id(b) == id(a)


def test_imul():
    g = Gt.get_generator()
    a = g * g
    b = Gt.get_generator()
    b *= g
    assert a == b


def test_double(group):
    """
    Does double() double correctly?
    """
    g = group.get_generator()
    a = g.get_double()
    g.double()
    assert a == g

    # Does it save the result in the same memory location?
    a = group.get_generator()
    b = a
    a.double()
    assert id(b) == id(a)


def test_square():
    """
    Does square() square correctly?
    """
    g = Gt.get_generator()
    a = g.get_square()
    b = Gt.get_generator()
    b.square()
    assert a == b

    # Does it save the result in the same memory location?

    a = Gt.get_generator()
    b = a
    a.square()
    assert id(b) == id(a)


def test_imul(group):
    """
    Does imul multiply correctly?
    """
    g = group.get_generator()
    a = g.mul(5)
    g *= 5
    assert a == g

    # Does it save the result in the same memory location?

    a = group.get_generator()
    b = a
    a *= 5
    assert id(b) == id(a)


def test_iexp():
    g = Gt.get_generator()
    a = g ** 100
    g **= 100
    assert a == g

    a = Gt.get_generator()
    b = a
    a **= 10
    assert id(b) == id(a)


def test_neg(group):
    """
    Does neg negate correctly?
    """
    g = group.get_generator()
    a = -g
    assert -a == g

    a = g.neg()
    assert a.neg() == g


def test_inverse():
    g = Gt.get_generator()
    a = g.get_inverse()
    g.inverse()
    assert a == g

    a = Gt.get_generator()
    b = a
    a.inverse()
    assert id(b) == id(a)


def test_g1_affine_inf():
    group = G1()
    inf = group.get_neutral_element()

    with pytest.raises(NoAffineCoordinateForECPoint) as ex:
        inf.get_affine_coordinates()


def test_ec_bin_translation(group):
    from timeit import default_timer as timer

    o = group.get_order()
    g = group.get_generator()
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
    g = Gt.get_generator()
    o = Gt.get_order()

    a = o.random()
    elem = g ** a

    # Test compresed
    binary = elem.to_binary()
    assert g.from_binary(binary) == elem

    # Test non-compressedj
    binary = elem.to_binary(compressed=False)
    assert g.from_binary(binary) == elem

