def main() -> int:
    try:
        # Import key modules to verify environment is set up correctly
        import domain.invoices  # noqa: F401
        import handlers  # noqa: F401
        import services  # noqa: F401
        import storage  # noqa: F401

        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
