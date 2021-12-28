import sys
import logging


class ErrorHandler:
    def __init__(self, exit_or_log, **logging_config):
        self.exit_or_log = exit_or_log
        self.database = {}
        if logging_config == {}:
            logging_config["format"] = "%(asctime)-15s [%(levelname)s] %(message)s"
        logging.basicConfig(**logging_config)

    def init_student(self, student_id: str):
        self.database[student_id] = ""

    def get_error(self, student_id):
        if not student_id in self.database.keys():
            return ""
        return self.database[student_id]

    def handle(self, msg="", exit_or_log=None, student_id="", max_len=200):
        action = self.exit_or_log if exit_or_log is None else exit_or_log

        if action == "exit":
            print(student_id + " " + msg)
            sys.exit(1)
        elif action == "log":
            if not student_id in self.database.keys():
                self.init_student(student_id)
            self.database[student_id] += str(msg) + str("\n")
            logging.error(
                student_id + " " + msg[:max_len] if len(msg) > max_len else msg
            )
        else:
            print("Cannot handle `" + action + "`. Check ErrorHandler setting.")
            sys.exit(1)

        if len(self.database[student_id]) > max_len:
            self.database[student_id] = self.database[student_id][:max_len]
