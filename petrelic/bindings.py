from petrelic._petrelic import ffi, lib

_FFI = ffi
_C = lib

RLC_OK = _C.get_rlc_ok()

class RelicInitializer:
    initialized = False

    def __init__(self):
        if not RelicInitializer.initialized:
            self.__initialize_relic()
            RelicInitializer.initialized = True

    def __initialize_relic(self):
        print("Initializing RELIC")
        if _C.core_init() != RLC_OK:
            raise RuntimeError("Could not initialize RELIC")

# Initializing RELIC
RelicInitializer()


