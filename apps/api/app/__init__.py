"""Backend application package bootstrap.

This project keeps two distinct import roots:

* ``apps/api``  -> the ``app`` package (web framework, routers, agents)
* ``<repo root>`` -> the ``evals`` and ``db`` packages (benchmark runner, seed data)

``apps/api/app/api/v1/evaluations.py`` imports ``evals.runner.evaluator`` and
``apps/api/app/main.py`` imports ``db.seed.seed_data``, so *both* roots must be
importable no matter how the process was started (uvicorn, pytest, Docker, IDE).

Two layouts have to be supported:

* local checkout : ``<root>/apps/api/app/__init__.py``
* Docker image   : ``/app/app/__init__.py`` (infra/Dockerfile.api flattens
  ``apps/api`` to ``/app`` and sets ``PYTHONPATH=/app``)

Rather than hard-coding a fixed number of parent hops, the repository root is
located by looking for the ``evals`` directory. That works for both layouts
without ever adding ``/`` to ``sys.path``.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()


def _import_roots() -> list[Path]:
    """Return the directories that must be on ``sys.path`` for this project."""
    roots = []

    # Root of the ``app`` package itself (``apps/api`` locally, ``/app`` in Docker).
    app_root = _HERE.parent.parent
    roots.append(app_root)

    # Root of the sibling top-level packages (``evals``, ``db``).
    for parent in _HERE.parents[:4]:
        if (parent / "evals").is_dir():
            roots.append(parent)
            break

    return roots


for _root in _import_roots():
    _root_str = str(_root)
    if _root_str not in sys.path:
        sys.path.insert(0, _root_str)