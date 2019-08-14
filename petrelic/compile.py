from cffi import FFI
import os

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
RELIC_BINDINGS_PATH = os.path.join(CURRENT_PATH, "_cffi_src")


def get_bindings_file(filename):
    src_path = os.path.join(RELIC_BINDINGS_PATH, filename)
    with open(src_path) as src_file:
        return src_file.read()


relic_bindings_defs = get_bindings_file("petrelic.h")
relic_bindings_src = get_bindings_file("petrelic.c")

_FFI = FFI()
_FFI.set_source(
    "petrelic._petrelic",
    relic_bindings_src,
    library_dirs=["/home/vagrant/local/lib"],
    include_dirs=["/home/vagrant/local/include"],
    libraries=["relic"],
)
_FFI.cdef(relic_bindings_defs)


if __name__ == "__main__":
    print("Compiling petrelic bindings for RELIC")
    _FFI.compile(verbose=True)
