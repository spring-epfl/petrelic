Installation
============

Coming soon:

You can install ``petrelic`` with ``pip``::

    pip install petrelic

Supported platforms
-------------------

Currently, ``petrelic`` was tested successfully with python 3.7 on Debian 10 on
x86_64 architecture. It might also work with Python 3.6 and 3.8, but no tests
were performed for these versions.

Building petrelic on Linux
--------------------------

``petrelic`` ships ``manylinux2010`` wheels which include all binary
dependencies. For users running a ``manylinux2010`` compatible distribution
(that is almost all distribution with a few exceptions, the most well known
being Alpine), ``petrelic`` can be installed trivially with ``pip``::

    pip install petrelic


Full manual install
-------------------

If you want to build ``petrelic`` fully manually, you will need to install
RELIC_ with some custom compilation options.

.. _RELIC: https://github.com/relic-toolkit/relic

The first step is to clone RELIC's Git repository, and to tweak the compilation
options of the preset `x64-pbc-bn382.sh` before executing it::

    git clone https://github.com/relic-toolkit/relic.git
    cd relic/presets
    sed 's/DSHLIB=OFF/DSHLIB=ON/' preset/x64-pbc-bls381.sh > preset/00custom.sh
    cd ..
    bash preset/00custom.sh -DCMAKE_INSTALL_PREFIX='/usr/local' .

Then RELIC can be build and installed with ``make``::

    make
    sudo make install

Once installed, ``petrelic`` can be installed with ``pip``::

    git clone https://github.com/spring-epfl/petrelic.git
    cd petrelic
    pip3 install -v -e '.[dev]'


Building the wheels manually
----------------------------

If you are using a non ``manylinux2010`` compatible distribution, or if you
prefer to compile ``petrelic`` yourself, you can do it by using the provided
building script ``build.sh``.

Running this script requires Docker. If Docker is not yet installed on your
system, please refer to its documentation_ to install it.

.. _documentation: https://docs.docker.com/get-docker/

The other typical building tools like ``make`` or ``gcc`` are already installed
in the ``manylinux2010`` Docker image, therefore no more dependencies are
required to build ``petrelic``.

Once Docker is installed on your system, you can build the wheel by running::

    sh build.sh

Once the script has finished running, which takes about 10 minutes, some wheels
will be copied on your working directory from the working directory in ``/tmp``,
which can be installed with ``pip``::

    pip install petrelic-0.1.0-cp37-cp37m-manylinux2010_x86_64.whl
