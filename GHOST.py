import subprocess
import requests
from colorama import init, Fore, Style
import os

# Initialize colorama
init(autoreset=True)

# Display a welcome message with ASCII art
def display_welcome():
    welcome_art = r"""
  ▄████  ██░ ██   ▒█████  ██████ ▄▄▄█████▓
 ██▒ ▀█▒▓██░ ██▒▒██▒  ██▒▒██    ▒ ▓  ██▒ ▓▒
▒██░▄▄▄░▒██▀▀██░▒██░  ██▒░ ▓██▄   ▒ ▓██░ ▒░
░▓█  ██▓░▓█ ░██ ▒██   ██░  ▒   ██▒░ ▓██▓ ░
░▒▓███▀▒░▓█▒░██▓░ ████▓▒░▒██████▒▒  ▒██▒ ░
 ░▒   ▒  ▒ ░░▒░▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░  ▒ ░░
  ░   ░  ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░▒  ░ ░    ░
░ ░   ░  ░  ░░ ░░ ░ ░ ▒  ░  ░  ░    ░
      ░  ░  ░  ░    ░ ░        ░
"""
    print(Fore.CYAN + welcome_art)
    print(Fore.GREEN + Style.BRIGHT + "Welcome to SQL Ghost: A Simple SQL Injection Tool\n")
    print(Fore.YELLOW + "Please enter a domain to begin subdomain enumeration.\n")

# Discover subdomains using subfinder
def find_subdomains(domain):
    print(Fore.CYAN + f"\nEnumerating subdomains for {domain} using subfinder...")
    try:
        result = subprocess.run(
            ["subfinder", "-d", domain, "-silent"],
            capture_output=True,
            text=True,
            check=True
        )
        subdomains = result.stdout.splitlines()
        print(Fore.GREEN + "\nDiscovered Subdomains:")
        for subdomain in subdomains:
            print(Fore.YELLOW + f" - {subdomain}")
        return subdomains
    except FileNotFoundError:
        print(Fore.RED + "Error: subfinder is not installed or not found in PATH.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error executing subfinder: {e}")
        return []

# Check if a URL is live
def is_live(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Run SQLMap for each live URL
def run_sqlmap(url, sql_command):
    print(Fore.BLUE + f"\nRunning SQLMap on {url}...")
    command = ["sqlmap", "-u", url, "--crawl=2", "--forms", "--batch", "--dbs"] + sql_command.split()
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print(Fore.RED + "SQLMap is not installed or not found in PATH. Please install it and try again.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error executing SQLMap on {url}: {e}")

# Show SQLMap help options if requested
def show_sqlmap_help():
    print(Fore.CYAN + "\nShowing SQLMap help options...\n")
    subprocess.run(["sqlmap", "-hh"])

# Main execution
if __name__ == "__main__":
    display_welcome()

    domain = input("Enter the domain to test for SQL injection: ").strip()
    if not domain:
        print(Fore.RED + "Invalid domain. Please enter a valid domain.")
        exit(1)

    # Step 1: Discover subdomains
    subdomains = find_subdomains(domain)

    # Step 2: Check live status and display only live URLs
    print(Fore.CYAN + "\nChecking connectivity for discovered subdomains...")
    live_urls = []
    for subdomain in subdomains:
        url = f"http://{subdomain}/"
        if is_live(url):
            print(Fore.GREEN + f"✔ {url} is live.")
            live_urls.append(url)
        else:
            print(Fore.RED + f"✘ {url} is not reachable.")

    # Step 3: Run SQL injection tests on live URLs
    if not live_urls:
        print(Fore.RED + "\nNo live subdomains found. Exiting.")
        exit(1)

    while True:
        sql_command = input(Fore.CYAN + "Enter additional SQLMap options (type 'help' to see all options, or leave empty for default): ").strip()
        if sql_command.lower() == "help":
            show_sqlmap_help()
        else:
            break

    for url in live_urls:
        run_sqlmap(url, sql_command)
