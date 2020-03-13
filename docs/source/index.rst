.. Petrelic documentation master file, created by
   sphinx-quickstart on Mon Feb 10 10:18:20 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Petrelic's documentation!
====================================

.. include::  ../../README.rst

.. toctree::
   :maxdepth: 2
   :caption: Basics

   quickstart
   install

Structure
---------

``petrelic`` provides three interfaces, ``petrelic.native``, ``petrelic.multiplicative``, and ``petrelic.additive`` to ``RELIC`` BLS-381 curve. In addition, it provides a binding to ``RELIC``'s big number (``Bn``) interface to ease integration between the two. In general, Python's integers can be substituted for ``Bn``s, and will be automatically converted. See the reference for more details on how to use these interfaces.

.. toctree::
   :maxdepth: 2
   :caption: Reference

   petrelic.bn
   petrelic.native
   petrelic.multiplicative
   petrelic.additive

