"""MIP legacy Streamlit helpers and Phase 5D demo shell.

Canonical local/public demo app: ``app/streamlit_app.py``

Run::

    poetry run streamlit run app/streamlit_app.py

Legacy JSON workflow shell: ``mip.app.streamlit_app`` via ``poetry run mip-app``.
"""

from mip.app.streamlit_app import CANONICAL_STREAMLIT_ENTRYPOINT

__all__ = ["CANONICAL_STREAMLIT_ENTRYPOINT"]
