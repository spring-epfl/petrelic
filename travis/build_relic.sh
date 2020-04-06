#!/usr/bin/env bash

RELIC_URL='https://github.com/relic-toolkit/relic.git'

set -e -x

git clone "${RELIC_URL}" ./relic

cd ./relic

sha256sum -c ../wheel/sha256sum.txt
if [ $? -ne 0 ]
then
    echo "WARNING! Relic's CMakeLists.txt has changed since the patch was created." >&2
fi

patch CMakeLists.txt ../wheel/CMakeLists.patch
if [ $? -ne 0 ]
then
    echo "ERROR! Patch failed to apply." >&2
    exit 1
fi

sed 's/DSHLIB=OFF/DSHLIB=ON/' preset/x64-pbc-bls12-381.sh > preset/00custom.sh

bash preset/00custom.sh -DCMAKE_INSTALL_PREFIX='/usr/local' .
make
sudo make install

cd ..
