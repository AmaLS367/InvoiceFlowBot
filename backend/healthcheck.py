def main() -> int:
    try:
        # Import key modules to verify environment is set up correctly
        import backend.domain.invoices  # noqa: F401
        import backend.handlers  # noqa: F401
        import backend.services  # noqa: F401
        import backend.storage  # noqa: F401

        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
