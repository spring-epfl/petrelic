petrelic
========

Simple Python wrapper around RELIC


Prerequisites
-------------

RELIC is required to use this project.

To install it: ::

    git clone https://github.com/relic-toolkit/relic.git
    cd relic
    cat << EOF > preset/00custom.sh
    #!/bin/bash
    cmake -DWSIZE=64 -DRAND=UDEV -DSHLIB=ON -DSTBIN=ON -DTIMER=CYCLE -DCHECK=off -DVERBS=off -DARITH=x64-asm-382 -DFP_PRIME=381 -DFP_METHD="INTEG;INTEG;INTEG;MONTY;LOWER;SLIDE" -DCOMP="-O3 -funroll-loops -fomit-frame-pointer -finline-small-functions -march=native -mtune=native" -DFP_PMERS=off -DFP_QNRES=on -DFPX_METHD="INTEG;INTEG;LAZYR" -DEP_PLAIN=off -DEP_SUPER=off -DPP_METHD="LAZYR;OATEP" $1
    EOF
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
