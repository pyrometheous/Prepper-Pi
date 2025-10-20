#!/usr/bin/env python3
"""
Automated Gutendex Downloader
Manages the entire lifecycle: start Docker containers, download books, optionally stop containers.

This script:
1. Checks if Docker is running
2. Starts Gutendex containers (if not already running)
3. Waits for Gutendex to be ready
4. Downloads books using specified parameters
5. Optionally stops containers when done

Usage:
    python automated_gutendex_download.py --mode popular --count 100
    python automated_gutendex_download.py --mode discover --genres-top 20 --keep-running
    python automated_gutendex_download.py --genres "Science Fiction,Fantasy" --count 50
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

import requests

# ---------------------------- Configuration ----------------------------

SCRIPT_DIR = Path(__file__).parent.resolve()
DOCKER_COMPOSE_FILE = SCRIPT_DIR / "docker-compose.gutendex.yml"
DOWNLOADER_SCRIPT = SCRIPT_DIR / "gutendex_selfhosted_to_kavita.py"
GUTENDEX_API_URL = "http://localhost:8000/books"
GUTENDEX_HEALTH_URL = "http://localhost:8000/books?page_size=1"

# Timeouts
CONTAINER_START_TIMEOUT = 300  # 5 minutes
CATALOG_DOWNLOAD_TIMEOUT = 900  # 15 minutes
API_READY_CHECK_INTERVAL = 5  # seconds


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# ---------------------------- Helper Functions ----------------------------


def log(msg: str, level: str = "INFO") -> None:
    """Print colored log messages."""
    colors = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "HEADER": Colors.HEADER,
    }
    color = colors.get(level, "")
    print(f"{color}[{level}]{Colors.ENDC} {msg}", flush=True)


def run_command(
    cmd: List[str], capture_output: bool = True, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command."""
    log(f"Running: {' '.join(cmd)}", "INFO")
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        return result
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e}", "ERROR")
        if e.stderr:
            log(f"Error output: {e.stderr}", "ERROR")
        raise


def check_docker_installed() -> bool:
    """Check if Docker is installed and accessible."""
    try:
        result = run_command(["docker", "--version"], check=False)
        if result.returncode == 0:
            log(f"Docker found: {result.stdout.strip()}", "SUCCESS")
            return True
    except FileNotFoundError:
        pass

    log("Docker not found! Please install Docker Desktop.", "ERROR")
    log("Download from: https://www.docker.com/products/docker-desktop", "INFO")
    return False


def check_docker_running() -> bool:
    """Check if Docker daemon is running."""
    try:
        result = run_command(["docker", "info"], check=False, capture_output=True)
        if result.returncode == 0:
            log("Docker daemon is running", "SUCCESS")
            return True
    except Exception:
        pass

    log("Docker daemon is not running!", "ERROR")
    log("Please start Docker Desktop and try again.", "INFO")
    return False


def check_docker_compose_installed() -> bool:
    """Check if Docker Compose is available."""
    # Try docker compose (V2)
    try:
        result = run_command(["docker", "compose", "version"], check=False)
        if result.returncode == 0:
            log(f"Docker Compose found: {result.stdout.strip()}", "SUCCESS")
            return True
    except Exception:
        pass

    # Try docker-compose (V1)
    try:
        result = run_command(["docker-compose", "--version"], check=False)
        if result.returncode == 0:
            log(f"Docker Compose found: {result.stdout.strip()}", "SUCCESS")
            return True
    except Exception:
        pass

    log("Docker Compose not found!", "ERROR")
    return False


def get_compose_command() -> List[str]:
    """Get the appropriate docker-compose command."""
    # Try V2 first
    try:
        result = run_command(
            ["docker", "compose", "version"], check=False, capture_output=True
        )
        if result.returncode == 0:
            return ["docker", "compose"]
    except Exception:
        pass

    # Fall back to V1
    return ["docker-compose"]


def check_containers_running() -> bool:
    """Check if Gutendex containers are already running."""
    try:
        compose_cmd = get_compose_command()
        result = run_command(
            compose_cmd
            + [
                "-f",
                str(DOCKER_COMPOSE_FILE),
                "ps",
                "--services",
                "--filter",
                "status=running",
            ],
            capture_output=True,
            check=False,
        )
        running_services = (
            result.stdout.strip().split("\n") if result.stdout.strip() else []
        )

        if "gutendex" in running_services and "postgres" in running_services:
            log("Gutendex containers are already running", "SUCCESS")
            return True

        return False
    except Exception as e:
        log(f"Could not check container status: {e}", "WARNING")
        return False


def start_containers() -> bool:
    """Start Gutendex Docker containers."""
    log("Starting Gutendex containers...", "HEADER")

    try:
        compose_cmd = get_compose_command()
        run_command(
            compose_cmd + ["-f", str(DOCKER_COMPOSE_FILE), "up", "-d"],
            capture_output=False,
        )
        log("Containers started successfully", "SUCCESS")
        return True
    except Exception as e:
        log(f"Failed to start containers: {e}", "ERROR")
        return False


def wait_for_api_ready(timeout: int = CATALOG_DOWNLOAD_TIMEOUT) -> bool:
    """Wait for Gutendex API to be ready and respond."""
    log("Waiting for Gutendex API to be ready...", "HEADER")
    log("(This may take 5-15 minutes on first run while catalog downloads)", "INFO")

    start_time = time.time()
    attempt = 0

    while time.time() - start_time < timeout:
        attempt += 1
        elapsed = int(time.time() - start_time)

        try:
            response = requests.get(GUTENDEX_HEALTH_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                log(f"✓ Gutendex API is ready! {count:,} books available", "SUCCESS")
                return True
        except requests.exceptions.ConnectionError:
            # Expected during startup
            pass
        except requests.exceptions.Timeout:
            log(f"API timeout on attempt {attempt} (after {elapsed}s)", "WARNING")
        except Exception as e:
            log(f"Unexpected error checking API: {e}", "WARNING")

        if attempt % 6 == 0:  # Log every ~30 seconds
            log(f"Still waiting... ({elapsed}s elapsed)", "INFO")

        time.sleep(API_READY_CHECK_INTERVAL)

    log(f"Timeout waiting for API after {timeout}s", "ERROR")
    log(
        "Check logs with: docker-compose -f docker-compose.gutendex.yml logs gutendex",
        "INFO",
    )
    return False


def download_books(
    mode: str,
    genres: Optional[str],
    count_per_genre: int,
    genres_top: int,
    out_dir: str,
    languages: str,
    sleep: float,
    no_collections: bool,
) -> bool:
    """Run the book download script."""
    log("Starting book download...", "HEADER")

    cmd = [
        sys.executable,  # Use same Python interpreter
        str(DOWNLOADER_SCRIPT),
        "--gutendex-url",
        GUTENDEX_API_URL,
        "--mode",
        mode,
        "--languages",
        languages,
        "--count-per-genre",
        str(count_per_genre),
        "--genres-top",
        str(genres_top),
        "--out",
        out_dir,
        "--sleep",
        str(sleep),
    ]

    if genres:
        cmd.extend(["--genres", genres])

    if no_collections:
        cmd.append("--no-collections")

    try:
        log(f"Running: {' '.join(cmd)}", "INFO")
        result = subprocess.run(cmd, check=True)
        log("Download completed successfully!", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Download failed with exit code {e.returncode}", "ERROR")
        return False
    except Exception as e:
        log(f"Unexpected error during download: {e}", "ERROR")
        return False


def stop_containers() -> bool:
    """Stop Gutendex Docker containers."""
    log("Stopping Gutendex containers...", "HEADER")

    try:
        compose_cmd = get_compose_command()
        run_command(
            compose_cmd + ["-f", str(DOCKER_COMPOSE_FILE), "down"], capture_output=False
        )
        log("Containers stopped successfully", "SUCCESS")
        return True
    except Exception as e:
        log(f"Failed to stop containers: {e}", "ERROR")
        return False


def show_container_logs(lines: int = 50) -> None:
    """Show recent container logs."""
    log("Recent Gutendex logs:", "INFO")
    try:
        compose_cmd = get_compose_command()
        run_command(
            compose_cmd
            + [
                "-f",
                str(DOCKER_COMPOSE_FILE),
                "logs",
                "--tail",
                str(lines),
                "gutendex",
            ],
            capture_output=False,
        )
    except Exception as e:
        log(f"Could not retrieve logs: {e}", "WARNING")


# ---------------------------- Main Logic ----------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Automated Gutendex Docker + Download Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download 100 most popular books, then stop containers
  python %(prog)s --mode popular --count 100

  # Auto-discover top 20 genres, 50 books each, keep running
  python %(prog)s --mode discover --genres-top 20 --count 50 --keep-running

  # Download specific genres
  python %(prog)s --genres "Science Fiction,Fantasy,Mystery" --count 30

  # Download to custom directory
  python %(prog)s --mode popular --count 50 --out ./MyLibrary

  # Just start containers (no download)
  python %(prog)s --start-only

  # Just stop containers
  python %(prog)s --stop-only
        """,
    )

    # Download mode options
    parser.add_argument(
        "--mode",
        type=str,
        choices=["genres", "popular", "discover"],
        default="popular",
        help="Download mode (default: popular)",
    )
    parser.add_argument(
        "--genres", type=str, help="Comma-separated genre list (for genres mode)"
    )
    parser.add_argument(
        "--count",
        "--count-per-genre",
        type=int,
        default=20,
        dest="count_per_genre",
        help="Books per genre (default: 20)",
    )
    parser.add_argument(
        "--genres-top",
        type=int,
        default=10,
        help="Number of top genres to auto-discover (default: 10)",
    )

    # Output options
    parser.add_argument(
        "--out",
        type=str,
        default="./KavitaLibrary",
        help="Output directory (default: ./KavitaLibrary)",
    )
    parser.add_argument(
        "--languages", type=str, default="en", help="Language codes (default: en)"
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Sleep between downloads in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--no-collections", action="store_true", help="Skip collection metadata"
    )

    # Container management
    parser.add_argument(
        "--keep-running",
        action="store_true",
        help="Keep containers running after download",
    )
    parser.add_argument(
        "--start-only",
        action="store_true",
        help="Only start containers, don't download",
    )
    parser.add_argument(
        "--stop-only",
        action="store_true",
        help="Only stop containers, don't start or download",
    )
    parser.add_argument(
        "--skip-wait",
        action="store_true",
        help="Skip waiting for API ready (use if already running)",
    )
    parser.add_argument(
        "--show-logs", action="store_true", help="Show container logs before exiting"
    )

    args = parser.parse_args()

    # Handle stop-only mode
    if args.stop_only:
        if stop_containers():
            return 0
        return 1

    # Pre-flight checks
    log("=" * 60, "HEADER")
    log("Automated Gutendex Downloader", "HEADER")
    log("=" * 60, "HEADER")

    if not check_docker_installed():
        return 1

    if not check_docker_running():
        return 1

    if not check_docker_compose_installed():
        return 1

    if not DOCKER_COMPOSE_FILE.exists():
        log(f"Docker Compose file not found: {DOCKER_COMPOSE_FILE}", "ERROR")
        return 1

    if not DOWNLOADER_SCRIPT.exists() and not args.start_only:
        log(f"Downloader script not found: {DOWNLOADER_SCRIPT}", "ERROR")
        return 1

    # Start containers if needed
    containers_already_running = check_containers_running()

    if not containers_already_running:
        if not start_containers():
            return 1

        # Wait for API to be ready
        if not args.skip_wait:
            if not wait_for_api_ready():
                log("Showing recent logs for debugging:", "INFO")
                show_container_logs(50)
                return 1
        else:
            log("Skipping API ready wait (--skip-wait)", "WARNING")
    else:
        log("Using already-running containers", "INFO")

        # Quick health check
        if not args.skip_wait:
            log("Checking API health...", "INFO")
            try:
                response = requests.get(GUTENDEX_HEALTH_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    count = data.get("count", 0)
                    log(f"✓ API is healthy: {count:,} books available", "SUCCESS")
                else:
                    log(f"API returned status {response.status_code}", "WARNING")
            except Exception as e:
                log(f"Could not verify API health: {e}", "WARNING")
                log("Continuing anyway...", "INFO")

    # Start-only mode
    if args.start_only:
        log("Containers started. Exiting (--start-only mode)", "SUCCESS")
        return 0

    # Download books
    success = download_books(
        mode=args.mode,
        genres=args.genres,
        count_per_genre=args.count_per_genre,
        genres_top=args.genres_top,
        out_dir=args.out,
        languages=args.languages,
        sleep=args.sleep,
        no_collections=args.no_collections,
    )

    # Show logs if requested
    if args.show_logs:
        show_container_logs(50)

    # Stop containers unless --keep-running
    if not args.keep_running and not containers_already_running:
        log("Stopping containers (use --keep-running to keep them alive)", "INFO")
        stop_containers()
    elif args.keep_running:
        log("Keeping containers running (--keep-running)", "INFO")
        log("To stop later: docker-compose -f docker-compose.gutendex.yml down", "INFO")

    if success:
        log("=" * 60, "SUCCESS")
        log("All operations completed successfully!", "SUCCESS")
        log("=" * 60, "SUCCESS")
        return 0
    else:
        log("=" * 60, "ERROR")
        log("Download failed. Check logs above for details.", "ERROR")
        log("=" * 60, "ERROR")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\nOperation cancelled by user", "WARNING")
        sys.exit(130)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback

        traceback.print_exc()
        sys.exit(1)
