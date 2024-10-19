from textual.app import App, ComposeResult
from textual.widgets import Button, Label, Input, ProgressBar
from textual_plotext import PlotextPlot
import time
import asyncio
import socket
import requests
from ping3 import ping
import os

class BandwidthTestApp(App):
    
    def compose(self) -> ComposeResult:
        # Input section for IP address
        yield Input(placeholder="Enter IP address or IP:PORT", id="ip_input")

        # Horizontal layout for buttons
        yield Button("Test ICMP", id="icmp_button")
        yield Button("Test UDP", id="udp_button")
        yield Button("Test TCP", id="tcp_button")
        yield Button("Test HTTP", id="http_button")  # HTTP Test button added

        # Vertical layout for progress bar and result label
        yield ProgressBar(id="progress_bar", total=100)
        yield Label("Result: ", id="result_label")
        # Plot area for bandwidth graph
        yield PlotextPlot(id="bandwidth_plot")

    async def on_mount(self) -> None:
        self.time_data = []
        self.bandwidth_data = []

    # Function to disable/enable buttons during tests
    def set_buttons_state(self, disabled: bool):
        buttons = [
            self.query_one("#icmp_button", Button),
            self.query_one("#udp_button", Button),
            self.query_one("#tcp_button", Button),
            self.query_one("#http_button", Button)  # HTTP button
        ]
        for button in buttons:
            button.disabled = disabled

    async def start_bandwidth_test_icmp(self, ip):
        self.set_buttons_state(True)
        result = await self.perform_icmp_test(ip)
        await self.update_result(result, "ICMP")
        self.set_buttons_state(False)

    async def start_bandwidth_test_udp(self, ip):
        self.set_buttons_state(True)
        result = await self.perform_udp_test(ip)
        await self.update_result(result, "UDP")
        self.set_buttons_state(False)

    async def start_bandwidth_test_tcp(self, ip):
        self.set_buttons_state(True)
        result = await self.perform_tcp_test(ip)
        await self.update_result(result, "TCP")
        self.set_buttons_state(False)

    async def start_bandwidth_test_http(self, ip):
        self.set_buttons_state(True)
        result = await self.perform_http_test(ip)
        await self.update_result(result, "HTTP")
        self.set_buttons_state(False)

    # ICMP bandwidth test using ping
    async def perform_icmp_test(self, ip):
        total_packets = 10
        start_time = time.time()

        for i in range(total_packets):
            try:
                elapsed_time = time.time() - start_time
                #using os ping to calculate ICMP ping
                response = ping(ip, unit="ms", timeout=1)
                if response is None:
                    return f"Failed: Timeout"
                bandwidth_mbps = 12 / response if response else 0
                self.update_progress(i + 1, total_packets)
                print(f"Bandwidth: {bandwidth_mbps:.6f} Mbps")
                self.time_data.append(elapsed_time)
                self.bandwidth_data.append(bandwidth_mbps)
            except Exception as e:
                return f"Failed: {str(e)}"
            await asyncio.sleep(0.5)

        return f"Success: {bandwidth_mbps:.3f} Mbps"
    
    # UDP bandwidth test
    async def perform_udp_test(self, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        total_packets = 10
        packet_size = 1024  # bytes
        start_time = time.time()

        for i in range(total_packets):
            try:
                sock.sendto(b"x" * packet_size, (ip, 80))
                elapsed_time = time.time() - start_time
                bandwidth = (packet_size * 8) / elapsed_time  # bits per second
                bandwidth_mbps = bandwidth / (1024 * 1024)  # Convert to Mbps
                self.time_data.append(elapsed_time)
                self.bandwidth_data.append(bandwidth_mbps)
                self.update_progress(i + 1, total_packets)
            except Exception as e:
                return f"Failed: {str(e)}"
            await asyncio.sleep(0.5)

        return f"Success: {bandwidth_mbps:.3f} Mbps"

    # TCP bandwidth test
    async def perform_tcp_test(self, ip):
        total_packets = 10
        packet_size = 1024  # bytes
        start_time = time.time()

        for i in range(total_packets):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, 80))
                sock.sendall(b"x" * packet_size)
                sock.close()
                elapsed_time = time.time() - start_time
                bandwidth = (packet_size * 8) / elapsed_time  # bits per second
                bandwidth_mbps = bandwidth / (1024 * 1024)  # Convert to Mbps
                self.time_data.append(elapsed_time)
                self.bandwidth_data.append(bandwidth_mbps)
                self.update_progress(i + 1, total_packets)
            except Exception as e:
                return f"Failed: {str(e)}"
            await asyncio.sleep(0.5)

        return f"Success: {bandwidth_mbps:.3f} Mbps"

    # HTTP bandwidth test
    async def perform_http_test(self, ip):
        total_requests = 10
        start_time = time.time()

        for i in range(total_requests):
            try:
                elapsed_time = time.time() - start_time
                response = requests.get(f"http://{ip}")
                if response.status_code != 200:
                    return f"Failed with status code {response.status_code}"
                self.update_progress(i + 1, total_requests)
                # Calculate bandwidth based on data received check if elapsed time is 0 to avoid division by zero
                if elapsed_time == 0:
                    bandwidth = 0
                else: 
                    bandwidth = (len(response.content) * 8) / elapsed_time  # bits per second
                bandwidth_mbps = bandwidth / (1024 * 1024)  # Convert to Mbps
                bandwidth_mbps = bandwidth_mbps * 100000
                print(f"Bandwidth: {bandwidth_mbps:.6f} Mbps")
                self.bandwidth_data.append(bandwidth_mbps)
                self.time_data.append(elapsed_time)
            except Exception as e:
                return f"Failed: {str(e)}"
            await asyncio.sleep(0.5)

        return f"Success: {bandwidth_mbps:.3f} Mbps"

    async def update_result(self, result, protocol):
        result_label = self.query_one("#result_label", Label)
        if "Success" in result:
            result_label.styles.color = "green"  # Color code for success
        else:
            result_label.styles.color = "red"  # Color code for failure
        result_label.update(f"{protocol} Test: {result}")
        await self.update_graph()

    def update_progress(self, current, total):
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress = int((current / total) * 100)
        progress_bar.progress = progress

    async def update_graph(self):
        graph = self.query_one("#bandwidth_plot", PlotextPlot)
        graph.refresh()
        plt = graph.plt  # Access the Plotext plt objectx
        plt.title("Bandwidth Over Time (Mbps)")
        # smooth the graph by interpolating the data so that the graph is more readable and smooth and not jagged
        # self.bandwidth_data = [self.bandwidth_data[0]] + self.bandwidth_data + [self.bandwidth_data[-1]]
        # self.time_data = [self.time_data[0]] + self.time_data + [self.time_data[-1]]
        plt.plot(self.time_data, self.bandwidth_data)
        # plt.plot(self.time_data, self.bandwidth_data)  # Plot the new data
        plt.xlabel("Time (s)")
        plt.ylabel("Bandwidth (Mbps)")
        plt.ylim(0, max(self.bandwidth_data) + 1)

    async def on_button_pressed(self, event):
        ip = self.query_one("#ip_input", Input).value
        if not ip:
            self.query_one("#result_label", Label).update("Please enter an IP address!")
            return

        if event.button.id == "icmp_button":
            await self.start_bandwidth_test_icmp(ip)
        elif event.button.id == "udp_button":
            await self.start_bandwidth_test_udp(ip)
        elif event.button.id == "tcp_button":
            await self.start_bandwidth_test_tcp(ip)
        elif event.button.id == "http_button":
            await self.start_bandwidth_test_http(ip)

if __name__ == "__main__":
    app = BandwidthTestApp()
    app.run()