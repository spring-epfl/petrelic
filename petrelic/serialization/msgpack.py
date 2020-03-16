# WARNING: work in progress. Do not use

import msgpack
import petlib.pack as pack

def pt_enc(obj):
    """Encoder for the wrapped points."""
    data = obj.to_binary()
    packed_data = msgpack.packb(data)
    return packed_data


def pt_dec(bptype):
    """Decoder for the wrapped points."""

    def dec(data):
        data_extracted = msgpack.unpackb(data)
        pt = bptype.from_binary(data_extracted)
        return pt

    return dec


# Register encoders and decoders for pairing points
# pack.register_coders(G1Element, 118, pt_enc, pt_dec(G1Element))
# pack.register_coders(G2Element, 119, pt_enc, pt_dec(G2Element))
# pack.register_coders(GTElement, 120, pt_enc, pt_dec(GTElement))
