# ──────────────────────────────────────────────────────────────────────────────
# Project metadata
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import sys
import inspect
import subprocess
from pathlib import Path
from typing import Optional

# Paths
HERE = Path(__file__).resolve().parent                # <repo>/docs
REPO_ROOT = HERE.parents[1]                           # <repo>/
SRC_DIR = REPO_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))
else:
    sys.path.insert(0, str(REPO_ROOT))

project   = "Pyaterochka API"
author    = "Miskler"
current_year = "2025"
copyright = f"{current_year}, {author}"

# Version without importing the package (safe for RTD)
def _get_version() -> str:
    # 1) env overrides (useful on CI/RTD)
    for key in ("PROJECT_VERSION", "READTHEDOCS_VERSION", "VERSION"):
        if os.getenv(key):
            return os.environ[key]
    # 2) try importlib.metadata
    try:
        from importlib.metadata import version  # type: ignore
        return version("pyaterochka_api")
    except Exception:
        pass
    # 3) fallback: import from package (may fail on RTD without deps)
    try:
        from chizhik_api import __version__  # type: ignore
        return __version__
    except Exception:
        return "0.0.0"

release: str = _get_version()
version: str = ".".join(release.split(".")[:3])

# ──────────────────────────────────────────────────────────────────────────────
# Extensions
# ──────────────────────────────────────────────────────────────────────────────
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.linkcode",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "enum_tools.autoenum",
    "jsoncrack_for_sphinx",
    # "myst_parser",  # если понадобится Markdown/MyST — просто раскомментируй
]

# Если есть тяжёлые/нестабильные зависимости — подмокай их, чтобы RTD не падал
autodoc_mock_imports: list[str] = [
    # "playwright", "pandas", ...
]

source_suffix = {
    ".rst": "restructuredtext",
}

# ──────────────────────────────────────────────────────────────────────────────
# Autosummary / Autodoc / Napoleon
# ──────────────────────────────────────────────────────────────────────────────
autosummary_generate = True
autosummary_imported_members = True
autosummary_ignore_module_all = False

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
    "special-members": "__call__",
    "exclude-members": "__weakref__",
}
autodoc_typehints = "signature"     # оставить type hints в сигнатурах
autodoc_preserve_defaults = True
autodoc_attr_value_repr = "repr"
autodoc_attr_value_cutoff = 80

# Napoleon (Google/Numpy docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_preprocess_types = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_attr_annotations = True

# ──────────────────────────────────────────────────────────────────────────────
# Cross-refs / TOC / Typing appearance
# ──────────────────────────────────────────────────────────────────────────────
toc_object_entries = True
toc_object_entries_show_parents = "hide"

add_module_names = False                         # compare() → Config
python_use_unqualified_type_names = True         # короткие типы в сигнатурах
multi_line_parameter_list = True
python_maximum_signature_line_length = 60

default_role = "any"                             # упрощает кросс-ссылки

nitpicky = True  # если хотите строгий режим
nitpick_ignore_regex = [
    ("py:class", r".*NoneType"),  # если всплывает для typing | None и т.п.
]

# ──────────────────────────────────────────────────────────────────────────────
# Intersphinx
# ──────────────────────────────────────────────────────────────────────────────
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "human_requests": ("https://miskler.github.io/human-requests/", None)
    # "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

# ──────────────────────────────────────────────────────────────────────────────
# Theme / HTML
# ──────────────────────────────────────────────────────────────────────────────
html_theme = "furo"
html_static_path = ["_static"]
templates_path = ["_templates"]
html_theme_options = {
    "light_logo": "logo-day.png",
    "dark_logo": "logo-night.png",
    "sidebar_hide_name": True,
    "source_repository": "https://github.com/Open-Inflation/pyaterochka_api",
    "source_branch": "main",
    "source_directory": "docs/",
    "globaltoc_collapse": False,
    "dark_css_variables": {},
    "light_css_variables": {
        # при желании можно подсветить бренд-цвет
        # "color-brand-primary": "#3B82F6",
        # "color-brand-content": "#3B82F6",
    },
}
# Подключение кастомных стилей (если появятся)
html_css_files = [
    # "tighten.css",
]

# ──────────────────────────────────────────────────────────────────────────────
# Linkcode → GitHub “View source” на точные строки
# ──────────────────────────────────────────────────────────────────────────────
def _git_revision() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT)
        return out.decode().strip()
    except Exception:
        return "main"

_GH_BASE = "https://github.com/Open-Inflation/pyaterochka_api"

def linkcode_resolve(domain: str, info: dict) -> Optional[str]:
    if domain != "py":
        return None
    modname = info.get("module")
    fullname = info.get("fullname")
    if not modname:
        return None
    try:
        # добираемся до объекта
        submod = sys.modules.get(modname)
        if submod is None:
            import importlib
            submod = importlib.import_module(modname)
        obj = submod
        for part in (fullname or "").split("."):
            obj = getattr(obj, part)
        fn = inspect.getsourcefile(obj) or inspect.getfile(obj)
        source, lineno = inspect.getsourcelines(obj)
    except Exception:
        return None
    rel = os.path.relpath(fn, start=str(REPO_ROOT))
    rev = _git_revision()
    end = lineno + max(len(source) - 1, 0)
    return f"{_GH_BASE}/blob/{rev}/{rel}#L{lineno}-L{end}"

# ──────────────────────────────────────────────────────────────────────────────
# JSONCrack for Sphinx (твои настройки сохранены)
# ──────────────────────────────────────────────────────────────────────────────
import os as _os
json_schema_dir = _os.path.join(HERE, "..", "..", "tests", "__snapshots__")

from jsoncrack_for_sphinx.config import (
    RenderMode,
    Directions,
    Theme,
    ContainerConfig,
    RenderConfig,
    SearchPolicy,
)

jsoncrack_default_options = {
    "render": RenderConfig(mode=RenderMode.OnClick()),
    "container": ContainerConfig(direction=Directions.DOWN, height="500", width="100%"),
    "theme": Theme.AUTO,
    "search_policy": SearchPolicy(custom_patterns=['{class_name}.{method_name}.json']),
    "autodoc_ignore": [
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# Extlinks (быстрые ссылки на GitHub)
# ──────────────────────────────────────────────────────────────────────────────
extlinks = {
    "issue":  (f"{_GH_BASE}/issues/%s", "#"),
    "pr":     (f"{_GH_BASE}/pull/%s", "PR #"),
    "commit": (f"{_GH_BASE}/commit/%s", ""),
}

# ──────────────────────────────────────────────────────────────────────────────
# Pygments / doctest / misc
# ──────────────────────────────────────────────────────────────────────────────
pygments_style = "sphinx"
pygments_dark_style = "native"
todo_include_todos = False

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ──────────────────────────────────────────────────────────────────────────────
# Setup hooks
# ──────────────────────────────────────────────────────────────────────────────
from sphinx.roles import XRefRole
def setup(app):
    app.add_role("pyclass", XRefRole("class"))
    app.add_role("pyfunc",  XRefRole("func"))
    # app.add_css_file("tighten.css")
