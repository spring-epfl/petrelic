Installation
============

Petrelic offers some Python binding for Relic. This library needs to be build
with some precise compilation flags. To use it with petrelic, a script to set
the correct compilation option is provided in `wheel/00custom.sh`, and is to be
run as the others presets for Relic. Also, the CMakeLists.txt of Relic needs to
be patched to take a compilation flag in consideration. The patch is provided
in: `wheel/CMakeLists.patch` and can be applied as any other patch::
    cd ${PATH_TO_RELIC}
    patch CMakeLists.txt "${PATH_TO_PETRELIC}/wheel/CMakeLists.patch"

Relic depends among other on GMP, which need to be installed either from
sources or from your distribution.

Some script to build Wheel packages are provided. They rely on manylinux2010
and Docker to run properly. Depending on your machine, building this wheel
takes about 10 minutes. To build this local wheel, run::
    cd ${PATH_TO_PETRELIC}
    sh build.sh

The resulting wheels contains Relic and GMP, and can be installed with pip as
normal::
    pip install petrelic-0.0.0-cp36-cp36m-manylinux2010_x86_64.whl


In the future, to simplify this installation, some Wheel packages are going to
provided for Linux and Mac OS X systems containing the embedded libraries Relic
and GMP, which will be able to be downloaded and installed with pip::
    pip install petrelic
