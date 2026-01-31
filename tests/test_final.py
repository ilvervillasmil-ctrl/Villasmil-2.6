Run pytest --cov=villasmil_omega --cov-report=term-missing
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/runner/work/Villasmil-2.6/Villasmil-2.6
plugins: cov-7.0.0
collected 31 items / 1 error

==================================== ERRORS ====================================
________________________ ERROR collecting test_basic.py ________________________
ImportError while importing test module '/home/runner/work/Villasmil-2.6/Villasmil-2.6/test_basic.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_basic.py:5: in <module>
    from villasmil_omega.meta_cierre import EstadoSuficiencia, decision_final
E   ImportError: cannot import name 'EstadoSuficiencia' from 'villasmil_omega.meta_cierre' (unknown location)
=========================== short test summary info ============================
ERROR test_basic.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.28s ===============================
Error: Process completed with exit code 2.
