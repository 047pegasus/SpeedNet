import asyncio
import time
from ping3 import ping
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Label, Static, ProgressBar
from textual.reactive import Reactive
from textual_plotext import PlotextPlot
from textual import events


class PingPanel(Static):
    """Panel to handle ping operation."""

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the Ping panel layout."""
        yield Label("Ping Test (IP:Port or IP)", id="ping-label")
        yield Input(placeholder="Enter IP or IP:Port", id="ping-input")
        yield Button("Start Ping", id="ping-button")
        yield Static(id="ping-result")  # Placeholder for results

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
            self.run_ping(address)

    def run_ping(self, ip_address: str, port: int = None):
        """Check if a service is online by using ping."""
        try:
            ping_result = ping(ip_address, timeout=2)
            if ping_result:
                message = f"Success: {ip_address} is reachable"
                color = "green"
            else:
                message = f"Failed: {ip_address} is unreachable"
                color = "red"
        except Exception as e:
            message = f"Error pinging {ip_address}: {str(e)}"
            color = "red"

        self.update_ping_result(message, color)

    def update_ping_result(self, message, color):
        result_panel = self.query_one("#ping-result", Static)
        result_panel.update(message)
        result_panel.styles.border_color = color  # Fix the dynamic color update


class BandwidthPanel(Static):
    """Panel to handle bandwidth calculation using ICMP-based round-trip time."""

    calculating: Reactive[bool] = Reactive(False)

    def __init__(self, ping_panel: PingPanel, graph_panel):
        super().__init__()
        self.ping_panel = ping_panel
        self.graph_panel = graph_panel

    def compose(self) -> ComposeResult:
        """Compose the Bandwidth panel layout."""
        yield Label("Bandwidth Test", id="bandwidth-label")
        yield Button("Start Bandwidth Test", id="bandwidth-button")
        yield ProgressBar(id="bandwidth-progress", total=100)
        yield Static(id="bandwidth-result")  # Placeholder for bandwidth results

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Start bandwidth calculation when the button is pressed."""
        if not self.calculating:
            ip_input = self.ping_panel.query_one("#ping-input", Input)
            address = ip_input.value
            if ":" in address:
                ip_address, _ = address.split(":")
            else:
                ip_address = address

            if ip_address:
                self.calculating = True
                asyncio.create_task(self.calculate_bandwidth(ip_address))
            else:
                self.update_bandwidth_result("Please enter a valid IP first.", "red")

    async def calculate_bandwidth(self, ip_address: str):
        """Calculate bandwidth using ICMP round-trip time asynchronously and update graph."""
        try:
            bandwidth_data = []
            time_data = []
            progress_bar = self.query_one("#bandwidth-progress", ProgressBar)

            start_time = time.time()

            for i in range(10):  # Simulate 10 seconds of bandwidth data collection
                elapsed_time = time.time() - start_time
                rtt = await self.get_icmp_rtt(ip_address)

                # Simple estimation: bandwidth inversely proportional to RTT
                bandwidth_mbps = 12 / rtt if rtt else 0

                bandwidth_data.append(bandwidth_mbps)
                time_data.append(elapsed_time)

                self.update_bandwidth_result(f"Current Bandwidth: {bandwidth_mbps:.2f} Mbps", "blue")
                progress_bar.update(progress=(i + 1) * 10)  # Update progress bar

                await asyncio.sleep(1)  # Simulate one second interval per measurement

            self.graph_panel.update_graph(time_data, bandwidth_data)
        except Exception as e:
            self.update_bandwidth_result(f"Error calculating bandwidth: {str(e)}", "red")
        finally:
            self.calculating = Reactive[False]

    async def get_icmp_rtt(self, ip_address: str) -> float:
        """Get ICMP round-trip time (RTT) in seconds."""
        try:
            rtt = ping(ip_address, timeout=1, size=56)
            if rtt:
                return rtt  # Return RTT in seconds
        except Exception as e:
            print(f"Error in pinging {ip_address}: {e}")
        return None

    def update_bandwidth_result(self, message, color):
        result_panel = self.query_one("#bandwidth-result", Static)
        result_panel.update(message)
        result_panel.styles.border_color = color  # Fix the dynamic color update


class GraphPanel(Static):
    """Panel to show a real-time graph using textual-plotext."""

    def __init__(self):
        super().__init__()
        self.plot = PlotextPlot()

    def compose(self) -> ComposeResult:
        """Compose the Graph panel layout."""
        yield Label("Bandwidth Over Time", id="graph-label")
        yield self.plot

    def update_graph(self, time_data, bandwidth_data):
        """Update the graph using textual-plotext."""
        self.plot.refresh()
        plt = self.plot.plt
        plt.title("Bandwidth Over Time")
        plt.plot(time_data, bandwidth_data)
        plt.xlabel("Time (s)")
        plt.ylabel("Bandwidth (Mbps)")
        plt.ylim(0, max(bandwidth_data) + 1)

class PingBandwidthApp(App):
    """Main TUI Application with Ping, Bandwidth, and Graph panels."""

    def compose(self) -> ComposeResult:
        """Compose the layout of the TUI with the three panels."""
        graph_panel = GraphPanel()
        ping_panel = PingPanel()
        bandwidth_panel = BandwidthPanel(ping_panel, graph_panel)

        yield ping_panel
        yield bandwidth_panel
        yield graph_panel

    async def on_key(self, event: events.Key) -> None:
        """Handle exit on pressing 'q'."""
        if event.key == "q":
            await self.shutdown()


if __name__ == "__main__":
    app = PingBandwidthApp()
    app.run()
