Wheels Building
===============

Petrelic is distributed as wheels with the libraries [Relic](https://github.com/relic-toolkit/relic) and [GMP](https://gmplib.org/) embedded. The wheels are build with `manylinux2014` and the libraries are embedded by auditwheel, QEMU is used to build non-native wheels.


Steps
-----

* Start a VM with Vagrant in the root directory of the git repository, and connect to it.

```
    vagrant up
    vagrant ssh
```

* Inside the VM, change the working directory to `/host`, and execute the build script.

```
    cd /host
    bash build.sh
```

* The script will download the sources of the dependencies and start a `manylinux2014` Docker container for each supported architecture (currently x86\_64 and aarch64). Inside the container, a second script will compile the dependencies and build the wheels for the supported Python versions (currently 3.7, 3.8, 3.9, and 3.10).

Once the script finished building the wheels, the build script will copy the wheels to the `wheelhouse` directory on the host.

* You can now logout from the vagrant VM and shut it down.

```
    vagrant halt
```

* The produced wheels will be contained in the `wheelhouse` directory.
