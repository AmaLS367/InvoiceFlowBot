"""
Healthcheck script for Docker container.

Performs minimal validation to ensure the bot environment is healthy.
"""


def main() -> int:
    """
    Perform minimal health check by importing key modules.

    Returns:
        0 if healthy, 1 if unhealthy.
    """
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

