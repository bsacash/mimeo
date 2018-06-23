#!/usr/bin/env python

import os
import time
from datetime import datetime

class BaseRule:
    def __init__(self, original_path, backup_path):
        self.original_path = original_path
        self.backup_path = backup_path

    # Creates a folder which is named by the current date/time in the location of the backup_path
    def _createDirectory(self):
        time = datetime.now().strftime('%Y-%m-%d\ %H_%M_%S')
        os.popen("mkdir {backup_path}/{time}".format(backup_path=self.backup_path.replace(" ","\ "),time=time))
        return "{backup_path}/{time}".format(backup_path=self.backup_path.replace(" ","\ "),time=time)

    def status(self):
        op = os.path.exists(self.original_path)
        bp = os.path.exists(self.backup_path)
        return {"Original Path":op, "Backup Path":bp}

    # Verify all rule parts are valid
    def check(self):
        valid = self.status()
        if sum(valid.values()) == 2:
            return True
        else:
            return False
    #TODO
    #def summary()
    #file size validation
    #log all messages into a log file

class FolderRule(BaseRule):
    def run(self):
        if self.check():
            backup_path_time = self._createDirectory()
            os.popen("cp {original_path}/* {backup_path_time}".format(original_path=self.original_path, backup_path_time=backup_path_time))
            print("Success: Folder Rule")
        else:
            print("ERROR: Check failed for Folder Rule.")
            print(self.status())


class FileRule(BaseRule):
    def __init__(self, original_path, backup_path, filename):
        BaseRule.__init__(self, original_path, backup_path)
        self.filename = filename

    def status(self):
        state = BaseRule.status(self)
        fn = os.path.exists(self.original_path + "/{filename}".format(filename=self.filename))
        state["Filname"] = fn
        return state

    # Verify all rule parts are valid
    def check(self):
        valid = self.status()
        if sum(valid.values()) == 3:
            return True
        else:
            return False

    def run(self):
        if self.check():
            backup_path_time = self._createDirectory()
            os.popen("cp {original_path}/{filename} {backup_path_time}".format(original_path=self.original_path,filename=self.filename,
                                                                      backup_path_time=backup_path_time))
            print("Success: File Rule")
            #print(summary)
        else:
            print("ERROR: Check failed for File Rule.")
            print(self.status())


class RecentRule(BaseRule):
    def __init__(self, original_path, backup_path, number):
        BaseRule.__init__(self, original_path, backup_path)
        self.number = number

    def status(self):
        state = BaseRule.status(self)
        #TODO: need try/except to deal with string/floats and turing string numbers to ints
        if isinstance(int(self.number), int) and int(self.number) > 0:
            state["Number"] = True
        else:
            state["Number"] = False
        return state

    # Verify all rule parts are valid
    def check(self):
        valid = self.status()
        if sum(valid.values()) == 3:
            return True
        else:
            return False

        # Backup the N most recent files from original_path to backup_path_time
    def run(self):
        if self.check():
            files = os.popen("ls -t {original_path} | head -{number}".format(original_path=self.original_path.replace(" ","\ "),number=self.number)).read()
            file_list = files.split("\n")[:-1] # list of N files to backup
            backup_path_time = self._createDirectory() #creates time base directory - should have access to backup_path
            for file in file_list:
                file = file.replace(" ","\ ") # add required escape characters
                file = file.replace("(","\(").replace(")","\)") # add required escape characters
                os.popen("cp {original_path}/{file} {backup_path_time}".format(original_path=self.original_path.replace(" ","\ "),file=file,
                                                                              backup_path_time=backup_path_time))
            print("Success: Recent Rule")
            #print(summary)
        else:
            print("ERROR: Check failed for Recent Rule.")
            print(self.status())

def process(rules_file):
    def _parse(rule):
        rule = rule.split(":", 1)[1:] # remove rule code
        rule = "".join(rule)
        rule = rule.split(",")
        rule = tuple(map(lambda x: x.strip(), rule))
        return rule

    # open and parse rules file
    rules = open(rules_file, "r").read()
    rules = rules.strip().split("\n")

    for rule in rules:
        # ignore comments and blank lines
        if len(rule) == 0:
            continue
        if rule[0] == "#":
            continue
        time.sleep(1)
        if rule[:2] == "R1":
            op, bp =  _parse(rule)
            r = FolderRule(op,bp)
            r.run()
        elif rule[:2] == "R2":
            op, bp, filename = _parse(rule)
            r = FileRule(op,bp,filename)
            r.run()
        elif rule[:2] == "R3":
            op, bp, number = _parse(rule)
            r = RecentRule(op,bp,number)
            r.run()
        else:
            print("Invalid Rule Code: {code}".format(code = rule[:2]))


def main():
    process("rules.txt")


if __name__ == "__main__":
    main()
