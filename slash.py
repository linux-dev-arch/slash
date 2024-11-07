import os
import shlex
import subprocess
import readline
import getpass
import socket
from colorama import Fore, Style, init
from pathlib import Path

# Initialize colorama for cross-platform color support
init()

# Color codes
PROMPT_COLOR = Fore.GREEN + Style.BRIGHT  # Green prompt
ERROR_COLOR = Fore.RED + Style.BRIGHT
RESET_COLOR = Style.RESET_ALL

# Get username and hostname
username = getpass.getuser()
hostname = socket.gethostname()

# List of built-in commands
BUILTINS = ["cd", "exit"]

# Function to handle built-in commands like cd
def execute_builtin_command(command, args):
    if command == "cd":
        # Change directory
        try:
            os.chdir(args[0] if args else os.path.expanduser("~"))
        except Exception as e:
            print(f"{ERROR_COLOR}cd: {e}{RESET_COLOR}")
    elif command == "exit":
        print("Exiting slash bye :) .")
        exit(0)
    else:
        return False
    return True

# Function to execute external commands
def execute_external_command(command, args):
    try:
        # Expand common aliases for Linux/Unix
        if command == "ls":
            command = "ls" if os.name != "nt" else "dir"
        result = subprocess.run([command] + args)
        return result.returncode
    except FileNotFoundError:
        print(f"{ERROR_COLOR}{command}: command not found{RESET_COLOR}")
    except Exception as e:
        print(f"{ERROR_COLOR}{command}: {e}{RESET_COLOR}")

# Autocomplete function
def completer(text, state):
    # Get all possible completions for the command
    commands = BUILTINS + get_system_commands()
    options = [cmd for cmd in commands if cmd.startswith(text)] + get_directory_completions(text)
    return options[state] if state < len(options) else None

# Function to retrieve all system commands available in PATH
def get_system_commands():
    paths = os.environ.get("PATH", "").split(os.pathsep)
    commands = set()
    for path in paths:
        if os.path.isdir(path):
            for filename in os.listdir(path):
                if os.access(os.path.join(path, filename), os.X_OK):
                    commands.add(filename)
    return sorted(commands)

# Function to get directory and file completions
def get_directory_completions(text):
    if "/" in text or "\\" in text:
        path = Path(text)
        directory = path.parent if path.suffix else path
    else:
        directory = Path.cwd()
    try:
        return [str(p) for p in directory.iterdir() if p.name.startswith(text)]
    except Exception:
        return []

# Main loop for the shell
def main():
    # Set up autocomplete
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    print("Welcome to the slash shell.Type exit to leave shell")
    while True:
        try:
            # Display prompt with colors
            current_dir = os.getcwd()
            prompt = f"{PROMPT_COLOR}{username}@{hostname}:{current_dir}{RESET_COLOR} $ "
            command_input = input(prompt)

            # Parse command and arguments
            tokens = shlex.split(command_input)
            if not tokens:
                continue
            command, *args = tokens

            # Execute built-in or external command
            if not execute_builtin_command(command, args):
                execute_external_command(command, args)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nExiting shell.")
            break

if __name__ == "__main__":
    main()
