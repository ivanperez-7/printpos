# PrintPOS — Agent Guide

## Setup

```powershell
pip install -r requirements.txt     # PySide6, fdb, haps, reportlab, etc.
pip install -r requirements-dev.txt # Nuitka, formatter, etc.
make                                # compile designer/*.ui + resources.qrc -> src/ui/
```

Always run from repo root. `PrintPOS.py` adds `src/` to `sys.path` at line 6 — do **not** install `src/` as a package; imports use short names (`from backends.Login import ...`).

## Architecture

- **DI**: `haps` library — `@base` (interfaces in `src/interfaces.py`), `@egg` (factories in `src/sql/core.py`), `IoC.autodiscover(['src.implementations'])` at app startup.
- **User context**: `src/context.py` — `threading.local()` object holding `conn` (fdb.Connection) and `user`.
- **DB**: Firebird via `fdb`, connection string `{host}/3050:PrintPOS.fdb` (default host `127.0.0.1` from `config.ini`). SQL schema in `resources/db/init.sql`.
- **Config**: `config.ini` read by `src/config.py` — exposes sections as properties via `INI` object.
- **Licensing**: LemonSqueezy API (`src/licensing.py`), machine-bound license stored at `%APPDATA%\PrintPOS\printpos.lic`.

## Generated (gitignored) files

- `src/ui/*.py` — compiled from `designer/*.ui` by `pyside6-uic`
- `src/ui/resources_rc.py` — compiled from `resources.qrc` by `pyside6-rcc`
- `PrintPOS.*/` — Nuitka dist directories

## Tests

All tests use `unittest.TestCase` (not pytest, despite `.vscode/settings.json`). Run individually:

```powershell
python -m tests.widgets_test
python -m tests.myutils_test
python -m tests.moneda_test
```

**Requires a live Firebird DB** at `127.0.0.1:3050/PrintPOS.fdb`. Test connections:
- `pablo / 1` (VENDEDOR role)
- `ivanperez / 123` (ADMINISTRADOR role)

Some tests **insert real data** (ventas, pagos, usuarios) without cleanup. Run only against a development DB.

## Key conventions

- `config.ini` at repo root — section `[RED]` has `nombre_servidor` (DB host) and `impresora`; `[SUCURSAL]` has address/phone.
- Style: Spanish names for modules/classes (`ManejadorVentas`, `VentanaPrincipal`, `crear`, `obtenerProducto`). Code comments in Spanish.
- Currency: `src/core/moneda.py::Moneda` — always 2-decimal precision, formatted as `1,234.56 MXN`.
- Printers configured via config.ini printer name — used with `QPrinter`/`reportlab` in `src/pdf/`.
- `user_context.conn` must be set before accessing any DB (see `bypass.py` for pattern).

## Build for distribution

```powershell
make install   # builds standalone .exe with Nuitka + PySide6 plugin
```
