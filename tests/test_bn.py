from petrelic.bn import Bn

import pytest
from copy import copy, deepcopy


def test_bn_constructors():
    assert Bn.from_decimal("100") == 100
    assert Bn.from_decimal("-100") == -100

    with pytest.raises(Exception):
        Bn.from_decimal("100ABC")

    with pytest.raises(Exception):
        Bn.from_hex("100ABCZ")

    assert Bn.from_hex(Bn(-100).hex()) == -100
    assert Bn(15).hex() == Bn(15).hex()

    with pytest.raises(Exception) as excinfo:
        Bn(-100).binary()
    assert "negative" in str(excinfo.value)

    # assert Bn.from_binary(Bn(-100).binary()) == 100
    assert Bn.from_binary(Bn(100).binary()) == Bn(100)
    assert Bn.from_binary(Bn(100).binary()) == 100

    with pytest.raises(Exception) as excinfo:
        s = 2 ** 65
        Bn(s)
    assert "does not fit" in str(excinfo.value)

    # assert Bn.from_binary(Bn(-100).binary()) != Bn(50)
    assert int(Bn(-100)) == -100

    assert repr(Bn(5)) == Bn(5).repr()
    assert repr(Bn(5)) == Bn(5).repr() == "Bn(5)"
    assert range(10)[Bn(4)] == 4

    d = {Bn(5): 5, Bn(6): 6}
    assert Bn(5) in d


def test_bn_prime():
    p = Bn.get_prime(128)
    assert p > Bn(0)
    assert p.is_prime()
    assert not Bn(16).is_prime()
    assert p.num_bits() > 127


def test_bn_arithmetic():
    assert Bn(1) + Bn(1) == Bn(2)
    assert Bn(1).int_add(Bn(1)) == Bn(2)

    assert Bn(1) + 1 == Bn(2)
    # assert (1 + Bn(1) == Bn(2))

    assert Bn(1) + Bn(-1) == Bn(0)
    assert Bn(10) + Bn(10) == Bn(20)
    assert Bn(-1) * Bn(-1) == Bn(1)
    assert Bn(-1).int_mul(Bn(-1)) == Bn(1)

    assert Bn(10) * Bn(10) == Bn(100)
    assert Bn(10) - Bn(10) == Bn(0)
    assert Bn(10) - Bn(100) == Bn(-90)
    assert Bn(10) + (-Bn(10)) == Bn(0)
    s = -Bn(100)
    assert Bn(10) + s == Bn(-90)
    assert Bn(10) - (-Bn(10)) == Bn(20)
    assert -Bn(-10) == 10
    assert Bn(-10).int_neg() == 10

    assert divmod(Bn(10), Bn(3)) == (Bn(3), Bn(1))
    assert Bn(10).divmod(Bn(3)) == (Bn(3), Bn(1))

    assert Bn(10) // Bn(3) == Bn(3)
    assert Bn(10).int_div(Bn(3)) == Bn(3)

    assert Bn(10) % Bn(3) == Bn(1)
    assert Bn(10).mod(Bn(3)) == Bn(1)

    assert Bn(2) ** Bn(8) == Bn(2 ** 8)
    assert pow(Bn(2), Bn(8), Bn(27)) == Bn(2 ** 8 % 27)

    pow(Bn(10), Bn(10)).binary()

    assert pow(Bn(2), 8, 27) == 2 ** 8 % 27

    assert Bn(3).mod_inverse(16) == 11

    with pytest.raises(Exception) as excinfo:
        Bn(3).mod_inverse(0)
        print("Got inverse")
    assert "No inverse" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        x = Bn(0).mod_inverse(Bn(13))
        print("!!! Got inverse", x)
    assert "No inverse" in str(excinfo.value)

    # with pytest.raises(Exception) as excinfo:
    #    x = Bn(0).mod_inverse(Bn(13))
    #    print("Got inverse", x)
    # assert 'No inverse' in str(excinfo.value)

    assert Bn(10).mod_add(10, 15) == (10 + 10) % 15
    assert Bn(10).mod_sub(100, 15) == (10 - 100) % 15
    assert Bn(10).mod_mul(10, 15) == (10 * 10) % 15
    assert Bn(-1).bool()


def test_bn_right_arithmetic():
    assert 1 + Bn(1) == Bn(2)

    assert -1 * Bn(-1) == Bn(1)

    assert 10 * Bn(10) == Bn(100)
    assert 10 - Bn(10) == Bn(0)
    assert 10 - Bn(100) == Bn(-90)
    assert 10 + (-Bn(10)) == Bn(0)
    s = -Bn(100)
    assert 10 + s == Bn(-90)
    assert 10 - (-Bn(10)) == Bn(20)

    assert divmod(10, Bn(3)) == (Bn(3), Bn(1))

    assert 10 // Bn(3) == Bn(3)

    assert 10 % Bn(3) == Bn(1)
    assert 2 ** Bn(8) == Bn(2 ** 8)

    assert 100 == Bn(100)

    pow(10, Bn(10))


def test_bn_allocate():
    # Test allocation
    n0 = Bn(10)
    assert True

    assert str(Bn()) == "0"
    assert str(Bn(1)) == "1"
    assert str(Bn(-1)) == "-1"

    assert Bn(15).hex() == "F"
    assert Bn(-15).hex() == "-F"

    assert int(Bn(5)) == 5
    assert Bn(5).int() == 5

    assert 0 <= Bn(15).random() < 15

    # Test copy
    o0 = copy(n0)
    o1 = deepcopy(n0)

    assert o0 == n0
    assert o1 == n0

    # Test nonzero
    assert not Bn()
    assert not Bn(0)
    assert Bn(1)
    assert Bn(100)


def test_bn_cmp():
    assert Bn(1) < Bn(2)
    assert Bn(1) <= Bn(2)
    assert Bn(2) <= Bn(2)
    assert Bn(2) == Bn(2)
    assert Bn(2) <= Bn(3)
    assert Bn(2) < Bn(3)


def test_extras():
    two = Bn(2)
    two2 = two.copy()
    assert two == two2


def test_odd():
    assert Bn(1).is_odd()
    assert Bn(1).is_bit_set(0)
    assert not Bn(1).is_bit_set(1)

    assert Bn(3).is_odd()
    assert Bn(3).is_bit_set(0)
    assert Bn(3).is_bit_set(1)

    assert not Bn(0).is_odd()
    assert not Bn(2).is_odd()

    assert Bn(100).is_bit_set(Bn(100).num_bits() - 1)
