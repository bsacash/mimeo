# Backup

Automate the process of backing up important files.

## Getting Started

Backup can copy file contents based on three different rules.
* FileRule: Backup a single file from one location to another
* FolderRule: Backup a directory or folder from one location to another
* RecentRule: Backup the N most recent files from one location to another

Modify the rules.json file to include as many rules as needed.

Examples:
```
{
  "type":"RecentRule",
  "original_path":"/Users/Me/Downloads",
  "backup_path": "/Users/Me/iCloud/Backup/Downloads",
  "number": 3,
  "description":"Backup the 3 most recent downloads to iCloud"
},
{
  "type":"FileRule",
  "original_path":"/Users/Me/Desktop",
  "backup_path": "/Users/Me/OneDrive/Backup/Desktop",
  "file": "notes.txt",
  "description":"Backup 'notes.txt' to OneDrive"
},
{
  "type":"FolderRule",
  "original_path":"/Users/Me/Documents/Important",
  "backup_path": "/Users/Me/Dropbox/Backups/Important",
  "description":"Backup 'Important' folder to Dropbox"
}
```

Each time a rule is carried out, a Date-Time folder will be created at the backup path location. This Date-Time folder is where to copied files will be placed.

### Prerequisites

* Python 3.x +

### Running

After modifying the rules.json file, run the backup.py file.
The rules file must be in the same directory as backup.py and must be named "rules.json".
```
$ python backup.py
```

## Errors

Backup verifies that paths, filenames, and numbers are valid before copying files. If an original path, backup path, filename, or number is not valid or does not exist for a particular rule, that rule will not be carried out.  Check the console to see what part of the rule is failing.
