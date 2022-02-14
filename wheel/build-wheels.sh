#!/bin/bash

PETRELIC_VERSION='0.1.5'
HOST_MOUNT='/host'
ARCH=$(uname -m)

if [[ 'x86_64' == "$ARCH" ]]
then
    MARCH='x86-64'
else
    MARCH='armv8-a'
fi

set -e -x

# Prepare clean copies.
cd /tmp
tar xf "${HOST_MOUNT}/wheel/gmp-${GMP_VERSION}.tar.xz"
cp -r "${HOST_MOUNT}/wheel/relic" /tmp/relic
cp -r "${HOST_MOUNT}" /tmp/petrelic

# Build and install GMP
cd gmp-"${GMP_VERSION}"
./configure --enable-fat CFLAGS="-O3 -funroll-loops -fomit-frame-pointer -finline-small-functions -march=${MARCH}"
make
make check
make install
make clean

# Install more modern version of cmake to build relic.
OLD_PATH="${PATH}"
PATH="/opt/python/cp37-cp37m/bin:${PATH}"
export PATH

pip install 'cmake==3.22.2'

# Build and install Relic
cd /tmp/relic

cp "${HOST_MOUNT}/wheel/00custom_${ARCH}.sh" preset/00custom.sh

mkdir build
cd build

bash ../preset/00custom.sh -DCMAKE_INSTALL_PREFIX='/usr/local' ..
make
make install
make clean

# Python 3.7 is still used at this point.
# Revert to initial PATH.
PATH="${OLD_PATH}"
export PATH

# Build the wheel

for PYTHON_VERSION in 'cp37-cp37m' 'cp38-cp38' 'cp39-cp39' 'cp310-cp310'
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
    auditwheel repair dist/petrelic-${PETRELIC_VERSION}-${PYTHON_VERSION}-linux_${ARCH}.whl

    # Restore PATH
    PATH="${OLD_PATH}"
    export PATH
done

# Copy the final wheeln on teh host.
cp -r wheelhouse "${HOST_MOUNT}/"
