import pytest

from petrelic.multiplicative.pairing import (
    G1,
    G1Element,
    G2,
    G2Element,
    Gt,
    GtElement,
    NoAffineCoordinateForECPoint,
)
from petrelic.bn import Bn


@pytest.fixture(params=[G1, G2, Gt])
def generator(request):
    return request.param.generator()


@pytest.fixture(params=[G1, G2, Gt])
def group(request):
    return request.param


@pytest.fixture(params=[G1Element, G2Element, GtElement])
def element(request):
    return request.param


def test_order(group):
    g = group.generator()
    o = group.order()
    assert g ** o == group.neutral_element()


def test_square_small(generator):
    a = 10
    h = generator ** a
    assert h.square() == generator ** (2 * a)


def test_square_small(generator):
    a = 10
    h = generator ** a
    h.isquare()
    assert h == generator ** (2 * a)


def test_square_random(group):
    g = group.generator()
    a = group.order().random()
    h = g ** a
    assert h.square() == g ** (2 * a)


def test_isquare_random(group):
    g = group.generator()
    a = group.order().random()
    h = g ** a
    h.isquare()
    assert h == g ** (2 * a)


def test_mul_random(group):
    g = group.generator()
    a = group.order().random()
    b = group.order().random()
    h = g ** a
    k = g ** b
    assert h * k == g ** (a + b)


def test_mul_large(group):
    g = group.generator()
    a = group.order() - 1
    b = group.order() - 2
    h = g ** a
    k = g ** b
    assert h * k == g ** -3


def test_imul(group):
    g = group.generator()
    a = group.order().random()
    b = group.order().random()
    h = g ** a
    k = g ** b
    assert h * k == g ** (a + b)
    h.imul(k)
    assert h == g ** (a + b)


def test_mul_pow(group):
    g = group.generator()
    assert g * g == g ** 2

    h = g ** group.order().random()
    assert h * h * h == h ** 3


def test_pow_identity(group):
    g = group.generator()
    assert group.neutral_element() == g ** 0


def test_pow_inverse(group):
    g = group.generator()
    ginv = g.inverse()
    assert ginv == g ** (-1)


def test_mul_different_type(group):
    g = group.generator()
    o = group.order()
    with pytest.raises(TypeError):
        g * o


def test_inverse(group):
    g = group.generator()
    a = group.order().random()
    h = g ** a

    assert h.inverse() == group.neutral_element() / h

    hinv = g ** (group.order() - a)
    assert h.inverse() == hinv


def test_iinverse(group):
    g = group.generator()
    a = group.order().random()
    h = g ** a
    hinv = g ** (group.order() - a)

    h.iinverse()
    assert h == hinv
