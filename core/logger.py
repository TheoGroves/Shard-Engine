import sys
from maths.python import Vec3

ANSI_RESET  = "\033[0m"
ANSI_GREY   = "\033[90m"
ANSI_CYAN   = "\033[36m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED    = "\033[31m"
ANSI_BRIGHT_RED = "\033[91m"

WHITE       = Vec3(1.0, 1.0, 1.0)
GREY        = Vec3(0.5, 0.5, 0.5)
CYAN        = Vec3(0.0, 0.7, 0.7)
GREEN       = Vec3(0.3, 0.6, 0.0)
YELLOW      = Vec3(0.9, 0.7, 0.0)
RED         = Vec3(0.7, 0.0, 0.0)
BRIGHT_RED  = Vec3(1.0, 0.0, 0.0)

class Logger:
    def __init__(self, console):
        self.console = console

    def log_trace(self, message):
        self.console.add_log(message, "trace")
        print(f"{ANSI_GREY}[TRACE] {message}{ANSI_RESET}")

    def log_debug(self, message):
        self.console.add_log(message, "debug")
        print(f"{ANSI_CYAN}[DEBUG]{ANSI_RESET} {message}")

    def log_info(self, message):
        self.console.add_log(message, "info")
        print(f"{ANSI_GREEN}[INFO]{ANSI_RESET} {message}")

    def log_warning(self, message):
        self.console.add_log(message, "warning")
        print(f"{ANSI_YELLOW}[WARNING]{ANSI_RESET} {message}")

    def log_error(self, message):
        self.console.add_log(message, "error")
        print(f"{ANSI_RED}[ERROR] {message}{ANSI_RESET}")

    def log_fatal(self, message):
        self.console.add_log(message, "fatal")
        print(f"{ANSI_BRIGHT_RED}[FATAL] {message} {ANSI_RESET}")
        sys.exit()