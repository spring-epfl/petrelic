#!/bin/sh

GMP_VERSION='6.2.1'
GMP_URL="https://ftp.gnu.org/gnu/gmp/gmp-${GMP_VERSION}.tar.xz"
RELIC_URL='https://github.com/relic-toolkit/relic.git'
ARCH_X86_64='x86_64'
ARCH_AARCH64='aarch64'
DOCKER_IMAGE_AARCH64="quay.io/pypa/manylinux2014_${ARCH_AARCH64}:latest"

if [ ! -e "./wheel/gmp-${GMP_VERSION}.tar.xz" ]
then
    curl -sSL -o "./wheel/gmp-${GMP_VERSION}.tar.xz" "${GMP_URL}"
fi

if [ -e  ./wheel/relic ]
then
    cd ./wheel/relic
    git pull
    cd ../..
else
    git clone "${RELIC_URL}" ./wheel/relic
fi

for ARCH in "${ARCH_X86_64}" "${ARCH_AARCH64}"
do
    DOCKER_IMAGE="quay.io/pypa/manylinux2014_${ARCH}:latest"
    docker pull "${DOCKER_IMAGE}"
    docker run --rm --name "manylinux-${ARCH}" -v"${PWD}/:/host" -e GMP_VERSION="${GMP_VERSION}" -it "${DOCKER_IMAGE}" /bin/bash /host/wheel/build-wheels.sh

    if [ ! $? -eq 0 ]
    then
        echo "Build failed for ${ARCH}." >&2
        exit 1
    fi
done

echo "That's all Folks!" >&2
