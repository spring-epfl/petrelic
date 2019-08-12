from .bindings import _FFI, _C

RLC_DIG = _C.get_rlc_dig()
RLC_OK = _C.get_rlc_ok()

DIGIT_MAXIMUM = 2 ** RLC_DIG - 1
