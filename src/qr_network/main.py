from .cli import app


def entry_point():
    import sys

    # If run without arguments (e.g. double-clicked app), default to GUI
    # Users can still pass --debug via CLI or shortcut if needed
    if len(sys.argv) == 1:
        sys.argv.append("gui")
    app()


if __name__ == "__main__":
    entry_point()
