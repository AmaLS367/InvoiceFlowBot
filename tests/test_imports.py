import importlib


def test_core_modules_importable() -> None:
    modules = (
        "bot",
        "config",
        "ocr.extract",
        "ocr.engine.router",
        "handlers.utils",
        "storage.db",
    )

    for name in modules:
        module = importlib.import_module(name)
        assert module is not None, f"Module {name} should import successfully"
