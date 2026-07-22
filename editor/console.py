from rendering import RenderEngine, LogLevel
from core.logger import *

PREFIX_ONLY = 0
ENTIRE_LOG = 1

class Log:
    LOG_TYPES = {
        "trace":   ("[TRACE]", GREY, ENTIRE_LOG),
        "debug":   ("[DEBUG]", CYAN, PREFIX_ONLY),
        "info":    ("[INFO]", GREEN, PREFIX_ONLY),
        "warning": ("[WARNING]", YELLOW, PREFIX_ONLY),
        "error":   ("[ERROR]", RED, ENTIRE_LOG),
        "fatal":   ("[FATAL]", BRIGHT_RED, ENTIRE_LOG)
    }

    def __init__(self, text: str, log_type: str):
        prefix, colour, colour_mode = self.LOG_TYPES.get(log_type.lower(), ("", WHITE, PREFIX_ONLY))

        self.prefix = prefix
        self.text = text
        self.colour = colour
        self.colour_mode = colour_mode

class Console:
    def __init__(self):
        self.render_engine = None

        self.logs = []
        self.scroll_to_bottom = False

    def set_render_engine(self, render_engine: RenderEngine):
        self.render_engine = render_engine

    def add_log(self, message: str, severity: str):
        self.logs.append(Log(message, severity))
        self.scroll_to_bottom = True

    def update(self, logger):
        for log in self.render_engine.consume_logs():
            if log.level == LogLevel.Trace:
                self.add_log(log.text, "trace")
                print(f"{ANSI_GREY}[TRACE] {log.text}{ANSI_RESET}")
            elif log.level == LogLevel.Debug:
                self.add_log(log.text, "debug")
                print(f"{ANSI_CYAN}[DEBUG]{ANSI_RESET} {log.text}")
            elif log.level == LogLevel.Info:
                self.add_log(log.text, "info")
                print(f"{ANSI_GREEN}[INFO]{ANSI_RESET} {log.text}")
            elif log.level == LogLevel.Warning:
                self.add_log(log.text, "warning")
                print(f"{ANSI_YELLOW}[WARNING]{ANSI_RESET} {log.text}")
            elif log.level == LogLevel.Error:
                self.add_log(log.text, "error")
                print(f"{ANSI_RED}[ERROR] {log.text}{ANSI_RESET}")
            elif log.level == LogLevel.Fatal:
                self.add_log(log.text, "fatal")
                print(f"{ANSI_BRIGHT_RED}[FATAL] {log.text} {ANSI_RESET}")
            else:
                self.add_log(f"Recieved log of unknown type: {log.text}", "warning")

        if self.render_engine.begin_window("Console"):
            self.render_engine.begin_child("Output", 0, 300)

            for log in self.logs:
                if log.colour_mode == PREFIX_ONLY:
                    self.render_engine.text_coloured(f"{log.prefix} ", log.colour)
                    self.render_engine.same_line()
                    self.render_engine.text(log.text)
                elif log.colour_mode == ENTIRE_LOG:
                    self.render_engine.text_coloured(f"{log.prefix} {log.text}", log.colour)
                else:
                    logger.log_warning("Log has undefined colour mode.")

            if self.scroll_to_bottom:
                self.render_engine.scroll_to_bottom()
                self.scroll_to_bottom = False

            self.render_engine.end_child()
        self.render_engine.end_window()

    def cleanup(self):
        for log in self.render_engine.consume_logs():
            if log.level == LogLevel.Trace:
                print(f"{ANSI_GREY}[TRACE] {log.text}{ANSI_RESET}")
            elif log.level == LogLevel.Debug:
                print(f"{ANSI_CYAN}[DEBUG]{ANSI_RESET} {log.text}")
            elif log.level == LogLevel.Info:
                print(f"{ANSI_GREEN}[INFO]{ANSI_RESET} {log.text}")
            elif log.level == LogLevel.Warning:
                print(f"{ANSI_YELLOW}[WARNING]{ANSI_RESET} {log.text}")
            elif log.level == LogLevel.Error:
                print(f"{ANSI_RED}[ERROR] {log.text}{ANSI_RESET}")
            elif log.level == LogLevel.Fatal:
                print(f"{ANSI_BRIGHT_RED}[FATAL] {log.text} {ANSI_RESET}")
            else:
                self.add_log(f"Recieved log of unknown type: {log.text}", "warning")
