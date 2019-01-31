#!/usr/bin/env python

import os
import time
from datetime import datetime

import shutil

class BaseRule:
    def __init__(self, original_path, backup_path):
        self.original_path = original_path
        self.backup_path = backup_path

    # Creates a folder which is named by the current date/time in the location of the backup_path
    def _createDirectory(self, mkdir=True):
        time = datetime.now().strftime('%Y-%m-%d %H_%M_%S')
        bpt = os.path.join(self.backup_path, time)
        if mkdir:
            os.mkdir(bpt)
        return bpt

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
            backup_path_time = self._createDirectory(mkdir=False)
            r = shutil.copytree(self.original_path, backup_path_time)
            if os.path.exists(r):
                print("Success: Folder Rule")
            else:
                print("Error: Write failed for Folder Rule")
        else:
            print("Error: Check failed for Folder Rule")
            print(self.status())


class FileRule(BaseRule):
    def __init__(self, original_path, backup_path, filename):
        BaseRule.__init__(self, original_path, backup_path)
        self.filename = filename

    def status(self):
        state = BaseRule.status(self)
        fn = os.path.exists(os.path.join(self.original_path, self.filename))
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
            r = shutil.copy2(os.path.join(self.original_path, self.filename), backup_path_time)
            if os.path.exists(r):
                print("Success: File Rule")
            else:
                print("Error: Write failed for File Rule")
            #print(summary)
        else:
            print("Error: Check failed for File Rule")
            print(self.status())


class RecentRule(BaseRule):
    def __init__(self, original_path, backup_path, number):
        BaseRule.__init__(self, original_path, backup_path)
        self.number = number

    def status(self):
        state = BaseRule.status(self)
        #TODO: need try/except to deal with string/floats and turming string numbers to ints
        if isinstance(int(self.number), int) and int(self.number) > 0:
            self.number = int(self.number)
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
            # this pulls .DS_Store - look into ignoring this in the future
            os.chdir(self.original_path)
            files = filter(os.path.isfile, os.listdir(self.original_path))
            files = [os.path.join(self.original_path, f) for f in files]
            files.sort(key=lambda x: os.path.getmtime(x))
            file_list = files[-self.number:] # list of N most recent files to backup


            backup_path_time = self._createDirectory()
            mini_log = []
            for index, file in enumerate(file_list):
                r = shutil.copy2(file, backup_path_time)
                if os.path.exists(r):
                    mini_log.append(True)
                else:
                    mini_log.append(False)
                    print("Error: Write failed for file {} in Recent Rule".format(index+1))

            if sum(mini_log) == len(mini_log):
                print("Success: Recent Rule")
                #print(summary)
            else:
                print("Error: Write failed for Recent Rule")
        else:
            print("Error: Check failed for Recent Rule")
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
