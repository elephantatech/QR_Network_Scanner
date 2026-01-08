import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .capture.scanner import QRCodeScanner
from .net.manager import NetworkManager
from .qr.parser import WiFiQRParser
from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    CAMERA_ERROR = 10
    NETWORK_ERROR = 20
    SCAN_TIMEOUT = 30
    USER_CANCEL = 40


app = typer.Typer()
console = Console()


@app.command()
def gui(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging to file"),
):
    """
    Launches the Graphical User Interface.
    """
    from .ui.app import main as gui_main

    gui_main(debug=debug)


@app.command()
def list_cameras():
    """
    Lists available cameras and their IDs.
    """
    from .utils import get_camera_names

    console.print(Panel.fit("Available Cameras", style="bold blue"))

    cameras = get_camera_names()

    if not cameras:
        console.print("[yellow]No cameras detected.[/yellow]")
        return

    # Create a simple table or list
    from rich.table import Table

    table = Table(title="Connected Cameras")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")

    for idx, name in enumerate(cameras):
        table.add_row(str(idx), name)

    console.print(table)


@app.command()
def scan(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    camera_id: int = typer.Option(0, "--camera", "-c", help="Camera ID to use"),
    timeout: float = typer.Option(
        60.0, "--timeout", "-t", help="Scan timeout in seconds"
    ),
    screen: bool = typer.Option(
        False, "--screen", "-s", help="Scan from screen instead of camera"
    ),
    file: str = typer.Option(
        None, "--file", "-f", help="Scan from image/PDF file instead of camera"
    ),
):
    """
    Scans a WiFi QR code and connects to the network.
    """

    # 1. Initialize
    try:
        scanner = QRCodeScanner(camera_id=camera_id)
        network_mgr = NetworkManager()

        console.print(Panel.fit("QR Network Scanner", style="bold blue"))

        # 2. Scan QR
        qr_data = None

        if screen:
            with console.status(
                "[bold green]Scanning screen(s) for WiFi QR Code...[/bold green]",
                spinner="dots",
            ):
                qr_data = scanner.scan_screen()
                if not qr_data:
                    console.print(
                        "[bold red]No QR code found on any screen.[/bold red]"
                    )
                    raise typer.Exit(code=ExitCode.CAMERA_ERROR)
        elif file:
            with console.status(
                f"[bold green]Scanning file '{file}' for WiFi QR Code...[/bold green]",
                spinner="dots",
            ):
                qr_data = scanner.scan_file(file)
                if not qr_data:
                    console.print(
                        f"[bold red]No QR code found in file '{file}'.[/bold red]"
                    )
                    raise typer.Exit(code=ExitCode.GENERAL_ERROR)
        else:
            with console.status(
                "[bold green]Scanning for WiFi QR Code... (Point camera at QR code)[/bold green]",
                spinner="dots",
            ):
                qr_data = scanner.scan_one(timeout=timeout)

        if not qr_data:
            console.print("[bold red]Scan timed out or cancelled. Exiting.[/bold red]")
            raise typer.Exit(code=ExitCode.SCAN_TIMEOUT)

        if verbose:
            console.print(f"[dim]Raw QR Data: {qr_data}[/dim]")

        # 3. Parse QR
        try:
            wifi_info = WiFiQRParser.parse(qr_data)
            ssid = wifi_info["ssid"]
            password = wifi_info.get("password", "")
            security = wifi_info.get("type", "WPA")
            hidden = wifi_info.get("hidden", False)

            hidden_str = " (Hidden)" if hidden else ""
            console.print(
                f"[bold]Found Network:[/bold] [green]{ssid}[/green] ({security}){hidden_str}"
            )

        except ValueError as e:
            console.print(f"[bold red]Error parsing QR code:[/bold red] {e}")
            raise typer.Exit(code=ExitCode.GENERAL_ERROR)

        # 4. Add Network
        if verbose:
            console.print(f"[dim]Adding network '{ssid}' to preferred list...[/dim]")

        success, output = network_mgr.add_network(
            ssid, password, security, hidden=hidden
        )
        if success:
            console.print(f"[green]✓[/green] Added network '{ssid}' to settings.")
        else:
            console.print(f"[red]✗[/red] Failed to add network: {output}")
            # We might continue and try to connect anyway?

        # 5. Connect
        console.print(f"[bold]Attempting to connect to '{ssid}'...[/bold]")

        # Check if already connected
        current = network_mgr.get_current_network()
        if current == ssid:
            console.print(f"[green]✓[/green] Already connected to '{ssid}'.")
            raise typer.Exit(code=ExitCode.SUCCESS)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Connecting...", total=None)
            success, output = network_mgr.activate_network(ssid, password)

        if success:
            console.print(
                Panel.fit(
                    f"[bold green]Successfully connected to {ssid}![/bold green]",
                    style="green",
                )
            )
        else:
            console.print(f"[bold red]Failed to connect:[/bold red] {output}")
            if "Error" in output:
                console.print(
                    "[yellow]Note: You might need to check your password or signal strength.[/yellow]"
                )
            raise typer.Exit(code=ExitCode.NETWORK_ERROR)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Scan cancelled by user.[/bold yellow]")
        raise typer.Exit(code=ExitCode.USER_CANCEL)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=ExitCode.GENERAL_ERROR)


if __name__ == "__main__":
    app()
