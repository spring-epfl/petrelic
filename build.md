Wheels Building
===============

Petrelic is distributed as wheels with the libraries [Relic](https://github.com/relic-toolkit/relic) and [GMP](https://gmplib.org/) embedded. The wheels are build with `manylinux1` and the libraries are embedded by using auditwheel.

The `manylinux1` Docker container rely on the legacy `vsyscall` API from the Linux Kernel. To ease the creation of wheels, a Vagrant configuration to build a VM with the emulation enabled is provided.

Steps
-----

Start a VM with Vagrant in the root directory of the git repository, and connect to it.
    vagrant up
    vagrant ssh

Inside the VM, change the working directory to `/host`, and execute the build script.
    cd /host
    bash build.sh

The script will create a temporary directory, download the sources of the dependencies and start a `manylinux1` Docker container. Inside the container, a second script will run to compile the dependencies and build the wheels for the supported Python versions. At the end, the first script will copy the wheels into the `/host` directory they will therefore be available from the host.

Remains to logout from the vagrant VM and shut it down.
    $ vagrant halt

The wheels are contained in the `wheelhouse` directory.
