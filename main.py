import time
import socket
import random
from rich.progress import Progress
from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Label, Static
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from PIL import Image
import requests


class PingPanel(Static):
    """Panel to handle ping operation."""

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the Ping panel layout."""
        yield Label("Ping Test (IP:Port)", id="ping-label")
        yield Input(placeholder="Enter IP:Port", id="ping-input")
        yield Button("Start Ping", id="ping-button")
        yield Static(id="ping-result")  # Placeholder for results
        yield Static(id="ping-progress")  # Placeholder for progress bar

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the ping operation when the button is pressed."""
        ip_input = self.query_one("#ping-input", Input)
        address = ip_input.value

        if ":" in address:
            ip_address, port = address.split(":")
            if ip_address and port.isdigit():
                self.run_ping(ip_address, int(port))
            else:
                self.update_ping_result("Please enter a valid IP:Port.", "red")
        else:
            self.update_ping_result("Please enter IP and Port in 'IP:Port' format.", "red")

    def run_ping(self, ip_address: str, port: int):
        """Check if a service is online by attempting a TCP connection."""
        with Progress() as progress:
            task = progress.add_task("Checking service...", total=4)
            self.update_ping_progress(progress, task)
            try:
                # Check if the port is open using socket connection
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    result = s.connect_ex((ip_address, port))
                    if result == 0:
                        message = f"Success: {ip_address}:{port} is online"
                        color = "green"
                    else:
                        message = f"Failed: {ip_address}:{port} is offline"
                        color = "red"
            except Exception as e:
                message = f"Error checking {ip_address}:{port}: {str(e)}"
                color = "red"

            self.update_ping_result(message, color)

    def update_ping_result(self, message, color):
        result_panel = self.query_one("#ping-result", Static)
        result_panel.update(Panel(message, border_style=color))

    def update_ping_progress(self, progress, task):
        progress_panel = self.query_one("#ping-progress", Static)
        for _ in range(4):
            progress.advance(task)
            progress_panel.update(Panel(f"Progress: {progress.tasks[task].completed}/{progress.tasks[task].total}"))


class BandwidthPanel(Static):
    """Panel to handle bandwidth calculation."""

    def __init__(self, ping_panel: PingPanel, graph_panel):
        super().__init__()
        self.ping_panel = ping_panel
        self.graph_panel = graph_panel

    def compose(self) -> ComposeResult:
        """Compose the Bandwidth panel layout."""
        yield Label("Bandwidth Test", id="bandwidth-label")
        yield Button("Start Bandwidth Test", id="bandwidth-button")
        yield Static(id="bandwidth-result")  # Placeholder for bandwidth results

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Start bandwidth calculation when the button is pressed."""
        ip_input = self.ping_panel.query_one("#ping-input", Input)
        address = ip_input.value
        if ":" in address:
            ip_address, _ = address.split(":")
            self.calculate_bandwidth(ip_address)
        else:
            self.update_bandwidth_result("Please enter a valid IP:Port first.", "red")

    def calculate_bandwidth(self, ip_address: str):
        """Calculate bandwidth by measuring download speed."""
        try:
            start_time = time.time()
            # Replace with a known test file or server for accurate measurement
            url = f"https://link.testfile.org/15MB"  # Ensure the server is running and has a test file
            response = requests.get(url, stream=True)
            total_bytes = 0

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    total_bytes += len(chunk)

            end_time = time.time()
            elapsed_time = end_time - start_time
            bandwidth_mbps = (total_bytes * 8) / (elapsed_time * 1024 * 1024)  # Convert to Mbps

            message = f"Bandwidth: {bandwidth_mbps:.2f} Mbps"
            self.update_bandwidth_result(message, "blue")

            # Update the graph panel with new data
            self.graph_panel.update_graph(bandwidth_mbps)
        except Exception as e:
            self.update_bandwidth_result(f"Error calculating bandwidth: {str(e)}", "red")

    def update_bandwidth_result(self, message, color):
        result_panel = self.query_one("#bandwidth-result", Static)
        result_panel.update(Panel(message, border_style=color))


class GraphPanel(Static):
    """Panel to plot a graph that updates with each bandwidth test."""

    def __init__(self):
        super().__init__()
        self.bandwidth_data = []

    def compose(self) -> ComposeResult:
        yield Label("Bandwidth Over Time", id="graph-label")
        yield Static(id="graph-image")  # Placeholder for graph image

    def update_graph(self, bandwidth: float):
        """Update the bandwidth graph with new data."""
        self.bandwidth_data.append(bandwidth)
        fig, ax = plt.subplots()
        ax.plot(self.bandwidth_data, color="blue", marker='o')
        ax.set_title("Bandwidth Over Time")
        ax.set_xlabel("Test Number")
        ax.set_ylabel("Bandwidth (Mbps)")

        # Convert the plot to an image
        canvas = FigureCanvas(fig)
        buffer = BytesIO()
        canvas.print_png(buffer)
        buffer.seek(0)

        # Use PIL to convert the image to something displayable
        image = Image.open(buffer)
        self.display_graph(image)

    def display_graph(self, image: Image.Image):
        """Display the graph image in the panel (convert to ASCII or use another method)."""
        graph_panel = self.query_one("#graph-image", Static)
        graph_panel.update("[Graph Placeholder]")  # Update this to actually display the graph.


class PingBandwidthApp(App):
    """Main TUI Application with Ping, Bandwidth, and Graph panels."""

    def compose(self) -> ComposeResult:
        """Compose the layout of the TUI with the two vertical splits and horizontal cuts."""
        graph_panel = GraphPanel()
        ping_panel = PingPanel()
        bandwidth_panel = BandwidthPanel(ping_panel, graph_panel)

        yield ping_panel
        yield bandwidth_panel
        yield graph_panel  # The right panel should take the remaining space (70% width)


if __name__ == "__main__":
    app = PingBandwidthApp()
    app.run()
