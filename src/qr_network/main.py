def entry_point():
    import sys

    # If arguments are provided, use CLI. Otherwise launch GUI.
    if len(sys.argv) > 1:
        from qr_network.cli import app

        app()
    else:
        from qr_network.ui.app import main as gui_main

        gui_main()


if __name__ == "__main__":
    entry_point()
