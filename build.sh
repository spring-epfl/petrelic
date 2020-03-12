#!/bin/sh

GMP_VERSION='6.2.0'
GMP_URL="https://ftp.gnu.org/gnu/gmp/gmp-${GMP_VERSION}.tar.bz2"
RELIC_URL='https://github.com/relic-toolkit/relic.git'
MANYLINUX_VERSION='manylinux2010'

cp -r . /tmp/petrelic
curl -L -o "/tmp/petrelic/wheel/gmp-${GMP_VERSION}.tar.bz2" "${GMP_URL}"
git clone "${RELIC_URL}" /tmp/petrelic/wheel/relic


docker run --rm --name manylinux -v'/tmp/petrelic/:/host' -it quay.io/pypa/${MANYLINUX_VERSION}_x86_64 /bin/bash /host/wheel/build-wheels.sh

if [ $? -eq 0 ]
then
    echo 'Wheels are in "/tmp/petrelic/wheelhouse/".' >&2
    cp -r /tmp/petrelic/wheelhouse ./
else
    echo 'Something went wrong.' >&2
    exit 1
fi
