from petrelic.petlib.pairing import G1Group, G1Elem, G2Group, G2Elem, GTGroup, GTElem
from petrelic.bn import Bn

import pytest


@pytest.fixture(params=["G1", "G2"])
def group(request):
    if request.param == "G1":
        return G1Group()
    if request.param == "G2":
        return G2Group()


def test_check_point(group):
    assert group.check_point(group.generator())
    assert group.check_point(100 * group.generator())


def test_check_point_gt():
    group = GTGroup()
    assert group.check_elem(group.generator())
    assert group.check_elem(group.generator() ** 100)


def test_hash_to_point(group):
    h1 = group.hash_to_point(b"Hello2")


@pytest.mark.skip(reason="not planning to implement this for now")
def test_ec_from_x(group):
    g = group.generator()
    x, y = g.get_affine()

    g1, g2 = group.get_points_from_x(x)
    assert g == g1 or g == g2


def test_ec_arithmetic(group):
    g = group.generator()
    assert g + g == g + g
    assert g + g == g.pt_double()
    assert g + g == Bn(2) * g
    assert g + g == 2 * g

    assert g + g != g + g + g
    assert g + (-g) == group.infinite()
    d = {}
    d[2 * g] = 2
    assert d[2 * g] == 2

    # Test long names
    assert (g + g).pt_eq(g + g)
    assert g + g == g.pt_add(g)
    assert -g == g.pt_neg()
    assert 10 * g == g.pt_mul(10)

    assert len(str(g)) > 0


def test_gt_multiplication():
    group = GTGroup()
    g = group.generator()
    assert g * g == g * g
    assert g * g == g.mul(g)
    assert g * g == g.sqr()
    assert g * g == g ** Bn(2)
    assert g * g == g ** 2

    assert g * g != g * g * g


def test_gt_unity():
    group = GTGroup()
    g = group.generator()
    unity = group.unity()

    assert g * unity == g
    assert unity * unity == unity


def test_gt_inv():
    group = GTGroup()
    g = group.generator()
    elem = g ** 1337

    assert elem * elem.inv() == group.unity()
    assert elem.inv() == elem ** (-1)


def test_gt_exponentiation():
    group = GTGroup()
    g = group.generator()

    assert g ** 3 == g * g * g
    assert g ** (-1) == g.inv()
    assert g ** 10 == g.exp(10)
    assert g ** Bn(10) == g.exp(Bn(10))


def test_g1_affine():
    group = G1Group()
    g = group.generator()
    x, y = g.get_affine()


def test_g1_export_length():
    group = G1Group()
    g = group.generator()
    assert len(g.export()) == 49


def test_ec_io(group):
    g = group.generator()

    i = group.infinite()
    assert len(i.export()) == 1
    assert g.from_binary(g.export(), group) == g
    assert g.from_binary(i.export(), group) == i


def test_gt_io(group):
    group = GTGroup()
    g = group.generator()

    i = group.unity()
    assert g.from_binary(g.export(), group) == g
    assert g.from_binary(i.export(), group) == i


def test_ec_sum(group):
    g = group.generator()
    assert group.sum([g] * 10) == (10 * g)

    order = group.order()
    h = order.random() * g
    assert group.wsum([Bn(10), Bn(20)], [g, h]) == 10 * g + 20 * h


def test_gt_prod():
    group = GTGroup()
    g = group.generator()
    assert group.prod([g] * 10) == (g ** 10)

    order = group.order()
    h = g ** order.random()
    assert group.wprod([Bn(10), Bn(20)], [g, h]) == g ** 10 * h ** 20


def test_pt_add_inplace(group):
    g = group.generator()
    """
    Does pt_add_inplace add correctly?
    """
    a = g.pt_add(g)
    g.pt_add_inplace(g)
    assert a == g

    """
    Does it save the result in the same memory location?
    """
    a = group.generator()
    b = a
    a.pt_add_inplace(a)
    assert id(b) == id(a)


def test_gt_mul_inplace():
    group = GTGroup()
    g = group.generator()
    a = g.mul(g)
    b = group.generator()
    b.mul_inplace(g)
    assert a == b


def test_pt_double_inplace(group):
    g = group.generator()
    """
    Does pt_double_inplace double correctly?
    """
    a = g.pt_double()
    g.pt_double_inplace()
    assert a == g

    """
    Does it save the result in the same memory location?
    """
    a = group.generator()
    b = a
    a.pt_double_inplace()
    assert id(b) == id(a)


def test_gt_sqr_inplace():
    group = GTGroup()
    g = group.generator()
    a = g.sqr()
    b = group.generator()
    b.sqr_inplace()
    assert a == b

    """
    Does it save the result in the same memory location?
    """
    a = group.generator()
    b = a
    a.sqr_inplace()
    assert id(b) == id(a)


def test_pt_mul_inplace(group):
    g = group.generator()
    """
    Does pt_mul_inplace multiply correctly?
    """
    a = g.pt_mul(5)
    g.pt_mul_inplace(5)
    assert a == g

    """
    Does it save the result in the same memory location?
    """
    a = group.generator()
    b = a
    a.pt_mul_inplace(5)
    assert id(b) == id(a)


def test_gt_exp_inplace():
    group = GTGroup()
    g = group.generator()
    a = g ** 100
    g.exp_inplace(100)
    assert a == g

    a = group.generator()
    b = a
    a.exp_inplace(10)
    assert id(b) == id(a)


def test_pt_neg_inplace(group):
    g = group.generator()
    """
    Does pt_neg_inplace negate correctly?
    """
    a = g.pt_neg()
    g.pt_neg_inplace()
    assert a == g

    """
    Does it save the result in the same memory location?
    """
    a = group.generator()
    b = a
    a.pt_neg_inplace()
    assert id(b) == id(a)


def test_gt_inv_inplace():
    group = GTGroup()
    g = group.generator()
    a = g.inv()
    g.inv_inplace()
    assert a == g

    a = group.generator()
    b = a
    a.inv()
    assert id(b) == id(a)


def test_g1_affine_inf():
    group = G1Group()
    inf = group.infinite()

    with pytest.raises(Exception) as excinfo:
        inf.get_affine()
    assert "EC Infinity" in str(excinfo.value)


def test_ec_bin_translation(group):
    from timeit import default_timer as timer

    o = group.order()
    g = group.generator()
    pt1000 = [o.random() * g for _ in range(1000)]

    exp = []
    for pt in pt1000:
        exp += [pt.export()]

    t0 = timer()
    for ept in exp:
        g.from_binary(ept, group)
    t1 = timer()
    print("\nParsed compressed Pt: %2.4f" % (t1 - t0))

    exp = []
    for pt in pt1000:
        exp += [pt.export(compressed=False)]

    t0 = timer()
    for ept in exp:
        g.from_binary(ept, group)
    t1 = timer()
    print("\nParsed uncompressed Pt: %2.4f" % (t1 - t0))


def test_gt_bin_translation():
    group = GTGroup()
    g = group.generator()
    o = group.order()

    a = o.random()
    elem = g ** a

    # Test compresed
    bin = elem.export()
    assert g.from_binary(bin) == elem

    # Test non-compressedj
    bin = elem.export(compressed=False)
    assert g.from_binary(bin) == elem
