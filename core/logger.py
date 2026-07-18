import sys

ANSI_RESET  = "\033[0m"
ANSI_GREY   = "\033[90m"
ANSI_CYAN   = "\033[36m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED    = "\033[31m"
ANSI_BRIGHT_RED = "\033[91m"

def log_trace(message):
    print(f"{ANSI_GREY}[TRACE] {message}{ANSI_RESET}")

def log_debug(message):
    print(f"{ANSI_CYAN}[DEBUG]{ANSI_RESET} {message}")

def log_info(message):
    print(f"{ANSI_GREEN}[INFO]{ANSI_RESET} {message}")

def log_warning(message):
    print(f"{ANSI_YELLOW}[WARNING]{ANSI_RESET} {message}")

def log_error(message):
    print(f"{ANSI_RED}[ERROR] {message}{ANSI_RESET}")

def log_fatal(message):
    print(f"{ANSI_BRIGHT_RED}[FATAL] {message} {ANSI_RESET}")
    sys.exit()