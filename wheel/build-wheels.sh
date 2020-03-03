#!/bin/bash

GMP_VERSION='6.2.0'
PETRELIC_VERSION='0.0.0'

RELIC_URL='https://github.com/relic-toolkit/relic.git'
HOST_MOUNT="/host"

set -e -x

# Install GMP
cd /tmp
tar xjf "/host/wheel/gmp-${GMP_VERSION}.tar.bz2"
cd gmp-"${GMP_VERSION}"
./configure
make
make install

# Install modern version of cmake to build relic.
OLD_PATH="${PATH}"
PATH="/opt/python/cp37-cp37m/bin:${PATH}"
export PATH

pip install cmake

# Build Relic
cp -r /host/wheel/relic /tmp/relic
cd /tmp/relic

# Custom modifications
sha256sum -c "${HOST_MOUNT}/wheel/sha256sum.txt"
if [ $? -ne 0 ]
then
    echo "WARNING! Relic's CMakeLists.txt has changed since the patch was created." >&2
fi

patch CMakeLists.txt "${HOST_MOUNT}/wheel/CMakeLists.patch"
if [ $? -ne 0 ]
then
    echo "ERROR! Patch failed to apply." >&2
    exit 1
fi

cp "${HOST_MOUNT}/wheel/00custom.sh" preset/00custom.sh

bash preset/00custom.sh -DCMAKE_INSTALL_PREFIX='/usr/local' .
make
make install

# Python 3.7 is still used at this point.
# Revert to initial PATH.
PATH="${OLD_PATH}"
export PATH

# Build the wheel

for PYTHON_VERSION in 'cp36-cp36m' 'cp37-cp37m' 'cp38-cp38'
do
    # Set new PATH
    OLD_PATH="${PATH}"
    PATH="/opt/python/${PYTHON_VERSION}/bin:${PATH}"
    export PATH

    # Install auditwheel for the correct version of python.
    pip install auditwheel

    # Install newer version of cmake
    cp -r "${HOST_MOUNT}" /tmp/petrelic
    cd /tmp/petrelic
    python setup.py bdist_wheel

    # Embbed libraries
    ls -l .
    ls -l dist
    auditwheel repair dist/petrelic-${PETRELIC_VERSION}-${PYTHON_VERSION}-linux_x86_64.whl

    # Restore PATH
    PATH="${OLD_PATH}"
    export PATH
done

# Copy the final wheeln on teh host.
cp -r wheelhouse "${HOST_MOUNT}/"
