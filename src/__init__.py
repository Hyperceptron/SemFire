# Package for AI Deception Detection Toolkit
try:
    from importlib.metadata import version as pkg_version, PackageNotFoundError
except Exception:  # pragma: no cover
    pkg_version = None  # type: ignore
    PackageNotFoundError = Exception  # type: ignore

try:
    __version__ = pkg_version("semfire") if pkg_version else "0.0.0"
except PackageNotFoundError:
    __version__ = "0.0.0"

from .semantic_firewall import SemanticFirewall

__all__ = [
    "SemanticFirewall",
]
