from textual.app import App, ComposeResult
from textual.widgets import Button, Label, Input, ProgressBar, Footer, Header, SelectionList, Pretty
from textual.widgets.selection_list import Selection
from textual.containers import Horizontal, Vertical, Grid
from textual_plotext import PlotextPlot
from textual.events import Mount
from textual import on
from textual.screen import Screen
import time
import asyncio
import socket
import requests
from ping3 import ping

PROTOCOL = ["ICMP", "UDP", "TCP", "HTTP"]
TEMP = []

class QuitScreen(Screen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()

class ProtocolErrored(Screen):
    """Screen with protocols that errored out and whose testing was unsuccessfull."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("The following protocols errored out during testing:", id="error_label"),
            Pretty(TEMP, id="error_list"),
            Button("Continue", variant="primary", id="ok_button"),
            classes="errored_protocols_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok_button":
            self.app.pop_screen()

class SpeedNet(App):
    CSS_PATH = "containers.tcss"
    BINDINGS = [("q", "request_quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header("SpeedNet: v0.1.1")

        # Input section for IP address and protocol selection
        yield Horizontal(
            Vertical(
                Label("Enter IP Address: ", id="ip_label"),
                Input(placeholder="Enter IP address or IP:PORT", id="ip_input"),
                classes="verticalinput",
            ),
            SelectionList(
                Selection("ICMP", 0),
                Selection("UDP", 1),
                Selection("TCP", 2),
                Selection("HTTP", 3),  # HTTP option added
                id="protocol_selection"
            ),
            classes="horizontalinput",
        )

        yield Horizontal(
            Button("Start Test", id="start_test_button"),  # Start Test button
            Button("Start Protocol Suite Test", id="start_suite_test_button"),  # Start Suite Test button
            Button("Reset Test Context", id="graph_reset_button"),  # Reset button for graph
            classes="horizontalbuttons",
        )

        # Vertical layout for progress bar and result label
        yield Horizontal(
            Label("Progress: ", id="progress_label"),
            ProgressBar(id="progress_bar", total=100),
            Label("Result: ", id="result_label"),
            classes="horizontalprogress",
        )
        
        # Plot area for bandwidth graph
        yield PlotextPlot(id="bandwidth_plot")

        yield Footer()
    
    def action_request_quit(self) -> None:
        self.push_screen(QuitScreen())
    
    async def on_mount(self) -> None:
        self.title = "SpeedNet v0.1.1"
        self.sub_title = "Network Protocol Analysis & Speed Test Utility"
        self.query_one(SelectionList).border_title = "Select Test Protocol"
        self.query_one("#start_suite_test_button").tooltip = "Starts a complete suite of tests for all the protocols on given address."
        self.query_one("#start_test_button").tooltip = "Starts the test for selected protocol on given address."
        self.query_one("#graph_reset_button").tooltip = "Resets the graph and test context."
        self.time_data = []
        self.bandwidth_data = []
        self.selected_protocol = []
        self.plotted_protocol = []

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.selected_protocol = self.query_one(SelectionList).selected
        print(f"Selected Protocol: {self.selected_protocol}")

    # Function to disable/enable buttons during tests
    def set_buttons_state(self, disabled: bool):
        buttons = [
            self.query_one("#start_test_button", Button),  # Start Test button
            self.query_one("#graph_reset_button", Button),  # Reset button
            self.query_one("#start_suite_test_button", Button)  # Start Suite Test button
        ]
        for button in buttons:
            button.disabled = disabled

    async def on_graph_reset_button(self, event):
        self.time_data = []
        self.bandwidth_data = [0]
        graph = self.query_one("#bandwidth_plot", PlotextPlot)
        graph.refresh()
        plt = graph.plt  # Access the Plotext plt objectx
        plt.clf()
        self.query_one("#result_label", Label).update("Graph Reset Successful!")
        self.query_one("#progress_bar", ProgressBar).progress = 0
        self.query_one("#ip_input", Input).value = ""
        self.query_one(SelectionList).deselect_all()
        self.selected_protocol = []
        self.plotted_protocol = []
        global TEMP, PROTOCOL
        PROTOCOL = ["ICMP", "UDP", "TCP", "HTTP"]
        TEMP = []

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
            isplotable = True
        else:
            result_label.styles.color = "red"  # Color code for failure
            isplotable = False
        result_label.update(f"{protocol} Test: {result}")
        if isplotable:
            await self.update_graph(protocol)
            self.plotted_protocol.append(protocol)

    def update_progress(self, current, total):
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress = int((current / total) * 100)
        progress_bar.progress = progress
    

    async def update_graph(self, protocol=""):
        graph = self.query_one("#bandwidth_plot", PlotextPlot)
        graph.refresh()
        plt = graph.plt  # Access the Plotext plt objectx
        plt.title("Throughput Over Time (Mbps)")
        # smooth the graph by interpolating the data so that the graph is more readable and smooth and not jagged
        # self.bandwidth_data = [self.bandwidth_data[0]] + self.bandwidth_data + [self.bandwidth_data[-1]]
        # self.time_data = [self.time_data[0]] + self.time_data + [self.time_data[-1]]
        
        plt.plot(self.time_data, self.bandwidth_data, marker="braille", label= protocol)  # Plot the new data
        plt.xlabel("Time (s)")
        plt.ylabel("Bandwidth (Mbps)")
        plt.ylim(0, max(self.bandwidth_data) + 1)
        self.bandwidth_data = [0]  # Reset the bandwidth data
        self.time_data = [0]

    async def on_button_pressed(self, event):
        ip = self.query_one("#ip_input", Input).value
        if not ip:
            self.query_one("#result_label", Label).update("Please enter an IP address!")
            return

        if event.button.id == "start_suite_test_button":
            self.selected_protocol = [0, 1, 2, 3]
            await self.start_bandwidth_test_icmp(ip)
            await self.start_bandwidth_test_udp(ip)
            await self.start_bandwidth_test_tcp(ip)
            await self.start_bandwidth_test_http(ip)
            global TEMP, PROTOCOL
            for i in self.selected_protocol:
                TEMP.append(PROTOCOL[i])
            for i in self.plotted_protocol:
                if i in TEMP:
                    TEMP.remove(i)
            #remove duplicates from the TEMP list
            TEMP = list(dict.fromkeys(TEMP))
            print(f"Errored out protocols during testing: {TEMP}")
            self.push_screen(ProtocolErrored())

        if event.button.id == "start_test_button":
            print(f"Starting test for IP: {ip} with protocols: {self.selected_protocol}")
            if 0 in self.selected_protocol:
                await self.start_bandwidth_test_icmp(ip)
            if 1 in self.selected_protocol:
                await self.start_bandwidth_test_udp(ip)
            if 2 in self.selected_protocol:
                await self.start_bandwidth_test_tcp(ip)
            if 3 in self.selected_protocol:
                await self.start_bandwidth_test_http(ip)
            for i in self.selected_protocol:
                TEMP.append(PROTOCOL[i])
            for i in self.plotted_protocol:
                if i in TEMP:
                    TEMP.remove(i)
            #remove duplicates from the TEMP list
            TEMP = list(dict.fromkeys(TEMP))
            print(f"Errored out protocols during testing: {TEMP}")
            self.push_screen(ProtocolErrored())

        if event.button.id == "graph_reset_button":
            await self.on_graph_reset_button(event)

if __name__ == "__main__":
    app = SpeedNet()
    app.run()