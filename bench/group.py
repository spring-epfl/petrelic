import timeit
import time
import secrets

from petrelic.petlib.pairing import G1Group, G2Group, GTGroup
from petrelic.bn import Bn

# WARNING: If changing from 1000 the results will no longer be in milliseconds
NR_ELEMS = 1000
REPEATS = 10


TABLE_WIDTH = 44
RESULT_FORMAT = "{op:32}  {time:02.8f}"


def print_time(op, expr):
    ts = timeit.repeat(expr, globals=globals(), number=1, repeat=5)
    print(RESULT_FORMAT.format(op=op, time=min(ts)))


def print_header(section):
    fstr = "{section:^" + str(TABLE_WIDTH) + "}"
    print_line(sym="=")
    print(fstr.format(section=section))
    print_line(sym="=")
    print("{op:32}  {time:>10}".format(op="Operation", time="Time (ms)"))
    print_line()


def print_line(sym="-"):
    print(sym * TABLE_WIDTH)


def print_footer():
    print_line()


def bench_group(name, group):
    global grp, generator, scalars, points, points2
    global input_strings, input_strings_long

    order = group.order()

    # Generate scalars and elements for benchmark
    grp = group
    generator = group.generator()
    scalars = [order.random() for _ in range(NR_ELEMS)]
    points = [order.random() * group.generator() for _ in range(NR_ELEMS)]
    points2 = [order.random() * group.generator() for _ in range(NR_ELEMS)]
    input_strings = [secrets.token_bytes(32) for _ in range(NR_ELEMS)]
    input_strings_long = [secrets.token_bytes(1024) for _ in range(NR_ELEMS)]

    print("\n")
    print_header("Group " + name)

    print_time("Square", "[p.pt_double() for p in points]")

    print_time("Multiplication", "[p + q for p, q in zip(points, points2)]")

    print_time("Exponentiation (generator)", "[s * generator for s in scalars]")

    print_time("Exponentiation (point)", "[s * p for s, p in zip(scalars, points)]")

    for bits in [2 ** x for x in range(3, 9)]:
        scalars = [Bn.get_random(bits) for _ in range(NR_ELEMS)]
        print_time(
            "    (scalar is {:>4} bits)".format(bits),
            "[s * p for s, p in zip(scalars, points)]",
        )

    if name != "GT":
        print_time(
            "Hash to point (32 bytes input)",
            "[grp.hash_to_point(s) for s in input_strings]",
        )

        print_time(
            "Hash to point (1024 bytes input)",
            "[grp.hash_to_point(s) for s in input_strings]",
        )

    print_time("Export", "[p for p in points]")

    print_footer()


def bench_pair():
    group1 = G1Group()
    group2 = G2Group()
    order = group1.order()

    global points, points2
    points = [order.random() * group1.generator() for _ in range(NR_ELEMS)]
    points2 = [order.random() * group2.generator() for _ in range(NR_ELEMS)]

    print("\n\n")
    print_header("Pairing: G1 x G2 -> GT")

    print_time("Pairing", "[p.pair(q) for p, q in zip(points, points2)]")

    print_footer()


if __name__ == "__main__":
    bench_group("G1", G1Group())
    bench_group("G2", G2Group())
    # bench_group("GT", GTGroup())
    bench_pair()
