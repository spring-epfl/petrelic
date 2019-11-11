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

Using a virtual environment is also advised: ::

    virtualenv -p /usr/bin/python3 venv/

Development
-----------

To start developing on `petrelic` create a local installation: ::

     pip3 install -v -e '.[dev]'

Zksk Integration
----------------

This library can be integrated with Zksk, to do so, the bn-wrapper branch of Zksk needs to be installed, and a global variable needs to be changed: ::

   cd ..
   git clone https://github.com/spring-epfl/zksk.git
   cd zksk
   git checkout bn-wrapper
   sed -i 's/BACKEND\s*=\s*"openssl"/BACKEND = "relic"/' zksk/bn.py
   cd ../petrelic
   . venv/bin/activate
   pip install -e ../zksk/

