#!/usr/bin/env python

import os
import errno
import json
import shutil
from collections import defaultdict
from datetime import datetime
from microlog import Logger

from helper import hash_file, hash_dir


class BaseRule:
    def __init__(self, original_path, backup_path, rule_id):
        self.original_path = original_path
        self.backup_path = backup_path
        self.rule_id = rule_id
       
    # Defines a directory which is named by the current date/time in the location of the backup_path
    def _defineDirectory(self):
        time = datetime.now().strftime('%Y-%m-%d %H_%M_%S')
        bpt = os.path.join(self.backup_path, self.subject, time)
        return bpt

    # Verify directory/file paths exists - return a dictionary of "fail", "pass" paths, and a "fail_count"
    def validate_locations(self, lst):
        d = defaultdict(list)
        fail_count = 0
        for item in lst:
            if os.path.exists(item):
                d["pass"].append(item)
            else:
                d["fail"].append(item)
                fail_count += 1
        d["fail_count"] = fail_count
        return dict(d)

    # Check hash of directory or file
    def check_hash(self, alpha_path, beta_path):
        if os.path.isfile(alpha_path) and os.path.isfile(beta_path):
            orig_hash = hash_file(alpha_path)
            copy_hash = hash_file(beta_path)
        elif os.path.isdir(alpha_path) and os.path.isdir(beta_path):
            orig_hash = hash_dir(alpha_path)
            copy_hash = hash_dir(beta_path)
        try:
            if orig_hash == copy_hash:
                logger.info(f"Rule {self.rule_id} - Original hash ({orig_hash}) matches copied hash ({copy_hash})")
            else:
                logger.error(f"Rule {self.rule_id} - Original hash ({orig_hash}) does not match copied hash ({copy_hash}) for '{beta_path}'")
        except:
            logger.error(f"Rule {self.rule_id} - Could not calculate hashes")


'''
FILE RULE
Copy a signle file from an original location to a backup location
'''
class FileRule(BaseRule):
    def __init__(self, original_path, backup_path, rule_id):
        BaseRule.__init__(self, original_path, backup_path, rule_id)
        self.filename = os.path.basename((self.original_path))
        self.subject = self.filename.replace(".", "_") + " [mimeo]"
        
    def run(self):
        check = self.validate_locations([self.original_path, self.backup_path])
        if check["fail_count"] > 0:
            for error in check["fail"]:
                logger.error(f"Rule {self.rule_id} - Location does not exist: {error}")
        else:
            backup_path_time = self._defineDirectory()

            
            try:
                os.makedirs(backup_path_time)
                r = shutil.copy2(self.original_path, backup_path_time)
            except OSError as e:
                r = ""
                if e.errno == errno.EEXIST: # file already exists error (this can happen if two rules try to write to the same location)
                    logger.error(f"Rule {self.rule_id} - The directory '{backup_path_time}'' already exists (most likely from another rule in this rule file)")
                else:
                    logger.error(f"Rule {self.rule_id} - There was an error when trying to create a backup location at '{backup_path_time}'")

            if os.path.exists(r): 
                logger.info(f"Rule {self.rule_id} - Copied '{self.original_path}' to '{backup_path_time}'")
                self.check_hash(self.original_path, os.path.join(backup_path_time, self.filename)) # verify hashses of orginal and copied content
            else:
                logger.error(f"Rule {self.rule_id} - Backup failed")

'''
RECENT RULE
Copy the N most recent files from an orignal location to a backup location
'''
class RecentRule(BaseRule):
    def __init__(self, original_path, backup_path, number, rule_id):
        BaseRule.__init__(self, original_path, backup_path, rule_id)
        self.number = number
        self.subject = os.path.basename(os.path.normpath((self.original_path))) + " [mimeo]"

    def run(self):
        check = self.validate_locations([self.original_path, self.backup_path])
        if check["fail_count"] > 0:
            for error in check["fail"]:
                logger.error(f"Rule {self.rule_id} - Location does not exist: {error}")
        else:
            # this pulls .DS_Store - look into ignoring this in the future
            current_path = os.getcwd()
            os.chdir(self.original_path)
            files = filter(os.path.isfile, os.listdir(self.original_path))
            files = [os.path.join(self.original_path, f) for f in files]
            files.sort(key=lambda x: os.path.getmtime(x))
            file_list = files[-self.number:] # list of N most recent files to backup
            os.chdir(current_path) #change back to mimeo path
            
            backup_path_time = self._defineDirectory()
            try:
                os.makedirs(backup_path_time)
            except OSError as e:
                if e.errno == errno.EEXIST: # file already exists error (this can happen if two rules try to write to the same location)
                    logger.error(f"Rule {self.rule_id} - The directory '{backup_path_time}' already exists (most likely from another rule in this rule file)")
                else:
                    logger.error(f"Rule {self.rule_id} - There was an error when trying to create a backup location at '{backup_path_time}'")

            # Copy each file
            for index, file_path in enumerate(file_list):
                r = shutil.copy2(file_path, backup_path_time)
                if os.path.exists(r):
                    logger.info(f"Rule {self.rule_id} - {index+1} of {len(file_list)}: Copied '{file_path}' from '{self.original_path}' to '{backup_path_time}'")

                    original_file = file_path
                    backup_file = os.path.join(self.backup_path, file_path)
                    self.check_hash(original_file, backup_file) # verify hashses of orginal and copied content
                else:
                     logger.error(f"Rule {self.rule_id} - {index+1} of {len(file_list)}: Backup failed for file '{file_path}'")

'''
FOLDER RULE
Copy a directory from an original location to a backup location
'''
class FolderRule(BaseRule):
    def __init__(self, original_path, backup_path, rule_id):
        BaseRule.__init__(self, original_path, backup_path, rule_id)
        self.subject = os.path.basename(os.path.normpath((self.original_path))) + " [mimeo]"

    def run(self):
        check = self.validate_locations([self.original_path, self.backup_path])
        if check["fail_count"] > 0:
            for error in check["fail"]:
                logger.error(f"Rule {self.rule_id} - Location does not exist: {error}")
        else:
            backup_path_time = self._defineDirectory()

            try:
                r = shutil.copytree(self.original_path, backup_path_time)
            except OSError as e:
                r = ""
                if e.errno == errno.EEXIST: # file already exists error (this can happen if two rules try to write to the same location)
                    logger.error(f"Rule {self.rule_id} - The directory '{backup_path_time}'' already exists (most likely from another rule in this rule file)")
                else:
                    logger.error(f"Rule {self.rule_id} - There was an error when trying to create a backup location at '{backup_path_time}'")
            
            if os.path.exists(r): 
                logger.info(f"Rule {self.rule_id} - Copied '{self.original_path}' to '{backup_path_time}'")
                self.check_hash(self.original_path, backup_path_time) # verify hashses of orginal and copied content
            else:
                logger.error(f"Rule {self.rule_id} - Backup failed")


def process(rules_file):
    rules_json = open(rules_file, "r").read()
    rules = json.loads(rules_json)["rules"]
    for rule in rules:
        if rule["type"] == "FileRule":
            f = FileRule(rule["original_path"], rule["backup_path"], rule["id"])
            f.run()
        elif rule["type"] == "FolderRule":
            f = FolderRule(rule["original_path"], rule["backup_path"], rule["id"])
            f.run()
        elif rule["type"] == "RecentRule":
            f = RecentRule(rule["original_path"], rule["backup_path"], rule["number"], rule["id"])
            f.run()
        else:
            logger.error(f"Invalid rule type for {rule['id']}")


def main():
    global logger
    logger = Logger(file = f"logs/{datetime.now().strftime('%Y-%m-%d')}")

    rules_file = "rules.json"
    logger.info(f"Processing {rules_file}")

    # Catch any error that would cause the file to stop
    try:
        process(rules_file)
        logger.info(f"Fininished processing {rules_file}")
    except:
        logger.error(f"Failed to finish processing {rules_file}")

    # Final error reporting
    errors = [log for log in logger.logs() if "[ERROR]" in log]
    if len(errors) == 0:
        logger.info(f"Ran {rules_file} successfully with no errors")
    elif len(errors) == 1:
        logger.critical(f"Ran {rules_file} with {len(errors)} error")
    else:
        logger.critical(f"Ran {rules_file} with {len(errors)} errors")
    if errors:
        print("\n* * * * * * * * * * * * * * * * * * * * * *")
        print("*       ERRORS FROM MOST RECENT RUN       *")
        print("* * * * * * * * * * * * * * * * * * * * * *")
        for error in errors:
            print(error)

if __name__ == "__main__":
    main()