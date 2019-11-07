petrelic
========

Simple Python wrapper around RELIC


Prerequisites
-------------

RELIC is required to use this project.

To install it: ::

    git clone https://github.com/relic-toolkit/relic.git
    cd relic
    sed 's/DSHLIB=OFF/DSHLIB=ON/' preset/x64-pbc-bls381.sh > preset/00custom.sh
    chmod +x preset/00custom.sh
    ./preset/00custom.sh -DCMAKE_INSTALL_PREFIX=/usr/local
    make
    sudo make install

The library path might also need to be updated: ::

    export LD_LIBRARY_PATH=/usr/local/lib:"$LD_LIBRARY_PATH"


Thanks to a bug in pytest, it is necessary to ignore mismatch import to run the tests: ::

   export PY_IGNORE_IMPORTMISMATCH=1

Using a virtual environment is also advised: ::

    virtualenv -p /usr/bin/python3 venv/

Development
-----------

To start developing on `petrelic` create a local installation: ::

     pip3 install -v -e '.[dev]'

