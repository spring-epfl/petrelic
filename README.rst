petrelic
========

``petrelic`` is a Python wrapper around `RELIC`_. It provides a simple python interface to the BLS-381 pairing and RELIC's big number class. Our goals is to make it easy to prototype new cryptographic applications in Python using RELIC as the backend. In the future we aim to support a few other pairing curves as well.

``petrelic`` provides native, multiplicative and additive interfaces to `RELIC`_. You can use the one that you find most comfortable. ``petrelic`` overloads Python's binary operators to make computation with pairings easy. For example, here is how you would compute and verify a BLS signature using the multiplicative interface:

.. code-block:: pycon

   >>> from petrelic.multiplicative.pairing import G1, G2, GT
   >>> sk = G1.order().random()
   >>> pk = G2.generator() ** sk

   >>> # Create the signature
   >>> m = b"Some message"
   >>> signature = G1.hash_to_point(m) ** sk

   >>> # Verify the signature
   >>> signature.pair(G2.generator()) == G1.hash_to_point(m).pair(pk)
   True

You can find more information in the `documentation`_.

You can install ``petrelic`` on Linux using:

.. code-block:: console

    $ pip install petrelic

For full details see `the installation documentation`_.

.. warning::
   Please don’t use this software for anything mission-critical. It is designed
   for rapid prototyping of cryptographic primitives using `RELIC`_. We offer no
   guarantees that the ``petrelic`` bindings are secure. We echo `RELIC`_ own
   warning: "RELIC is at most alpha-quality software. Implementations may not be
   correct or secure and may include patented algorithms. ... Use at your own risk."

.. _`RELIC`: https://github.com/relic-toolkit/relic
.. _`documentation`: https://petrelic.readthedocs.io/
.. _`the installation documentation`: https://petrelic.readthedocs.io/en/latest/installation/
