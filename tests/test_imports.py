import importlib


def test_core_modules_importable() -> None:
    modules = (
        "bot",
        "backend.config",
        "backend.ocr.extract",
        "backend.ocr.engine.router",
        "backend.handlers.utils",
        "backend.storage.db",
    )

    for name in modules:
        module = importlib.import_module(name)
        assert module is not None, f"Module {name} should import successfully"
