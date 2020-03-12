Installation
============

Coming soon:

You can install `petrelic` with `pip`:::

    pip install petrelic

Supported platforms
-------------------

Currently, `petrelic` was tested successfully with python 3.7 on Debian 10 on
x86_64 architecture. It might also work with Python 3.6 and 3.8, but no tests
were performed for these versions.

Building petrelic on Linux
--------------------------

`petrelic` ships `manylinux2010` wheels which include all binary dependencies.
For users running a `manylinux2010` compatible distribution (that is almost
all distribution with a few exceptions, the most well known being Alpine),
`petrelic` can be installed trivially with `pip`:::

    pip install petrelic


Building the wheels manually
----------------------------

If you are using a non `manylinux2010` compatible distribution, or if you
prefer to compile `petrelic` yourself, you can do it by using the provided
building script `build.sh`.

Running this script requires Docker. If Docker is not yet installed on your
system, please refer to its documentation_ to install it.

.. _documentation: https://docs.docker.com/get-docker/

The other typical building tools like `make` or `gcc` are already installed in
the `manylinux2010` Docker image, therefore no more dependencies are required
to build `petrelic`.

Once Docker is installed on your system, you can build the wheel by running:::

    sh build.sh

Once the script has finished running, which takes about 10 minutes, some wheels
will be copied on your working directory from the working directory in `/tmp`,
which can be installed with `pip`:::

    pip install petrelic-0.1.0-cp37-cp37m-manylinux2010_x86_64.whl


Full manual install
-------------------

If you want to build petrelic fully manually, you will need to install RELIC_
with some custom compilation options. The `CMakeLists.txt` file of RELIC also
needs to be patched.

.. _RELIC: https://github.com/relic-toolkit/relic

The first step will therefore be to clone their Git repositories.::

    git clone https://github.com/relic-toolkit/relic.git
    git clone https://github.com/spring-epfl/petrelic.git

For the rest of these instructions, we will assume that the variables:

- `RELIC` is the path to the directory containing RELIC source code.
- `PETRELIC` is the path to the directory containing petrelic source code.

The patch for RELIC's `CMakeLists.txt` is `wheel/CMakeLists.patch` and can be
applied with:::

    patch ${RELIC}/CMakeLists.txt "${PETRELIC}/wheel/CMakeLists.patch"

The script to call `cmake` with the correct compilation options can be run as
the others presets from RELIC, this file is `wheel/00custom.sh`, it can be
copied to the directories containing the other presets and executed from the
root of RELIC source directory.::

    cp ${PETRELIC}/wheel/00custom.sh ${RELIC}/preset/00custom.sh
    cd ${RELIC}
    bash preset/00custom.sh -DCMAKE_INSTALL_PREFIX='/usr/local' .

Then RELIC can be build with make:::
    make
    sudo make install

Once installed, petrelic can be installed with pip:::
    cd ${PETRELIC}
    pip3 install -v -e '.[dev]'
