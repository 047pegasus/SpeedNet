import time
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console
from ping3 import ping

console = Console()


def ping_test(ip_address: str, num_pings: int = 5):
    """Perform a ping test on the given IP address."""
    results = []
    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            transient=True,
    ) as progress:
        task = progress.add_task(f"Pinging {ip_address}", total=num_pings)

        for _ in range(num_pings):
            try:
                response_time = ping(ip_address, timeout=2)
                if response_time is None:
                    results.append("Timeout")
                    progress.console.print(f"[red]Timeout[/red] pinging {ip_address}")
                else:
                    response = f"{response_time * 1000:.2f} ms"
                    results.append(response)
                    progress.console.print(f"[green]{response}[/green]")
            except Exception as e:
                results.append(str(e))
                progress.console.print(f"[red]Ping error: {str(e)}[/red]")

            progress.advance(task)
            time.sleep(1)  # to simulate time between pings

    return results


def display_summary(results, ip_address):
    """Display the summary of the ping results."""
    success_pings = [r for r in results if "ms" in r]
    timeout_pings = results.count("Timeout")

    console.print(f"\n[bold blue]Summary for {ip_address}:[/bold blue]")
    console.print(f"Total pings: {len(results)}")
    console.print(f"Successful pings: {len(success_pings)}")
    console.print(f"Timeouts: {timeout_pings}")

    if success_pings:
        avg_time = sum(float(r.split()[0]) for r in success_pings) / len(success_pings)
        console.print(f"Average Response Time: [green]{avg_time:.2f} ms[/green]")
    else:
        console.print("[red]No successful pings.[/red]")


if __name__ == "__main__":
    console.print("[bold]Ping Test TUI[/bold]")
    ip_address = console.input("Enter IP address to ping: ")

    ping_results = ping_test(ip_address)
    display_summary(ping_results, ip_address)
