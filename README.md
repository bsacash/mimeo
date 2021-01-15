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
  "id": 1,
  "type":"RecentRule",
  "original_path":"/Users/Me/Downloads",
  "backup_path": "/Users/Me/iCloud/Backup/Downloads",
  "number": 3,
  "description":"Backup the 3 most recent downloads to iCloud"
},
{
  "id": 2,
  "type":"FileRule",
  "original_path":"/Users/Me/Desktop/notes.txt",
  "backup_path": "/Users/Me/OneDrive/Backup/Desktop",
  "description":"Backup 'notes.txt' to OneDrive"
},
{
  "id": 3,
  "type":"FolderRule",
  "original_path":"/Users/Me/Documents/Important",
  "backup_path": "/Users/Me/Dropbox/Backups/Important",
  "description":"Backup 'Important' folder to Dropbox"
}
```

Each time a rule is carried out, a directory will be made with a preceeding underscore containing a Date-Time folder with the copied contents. This Date-Time folder is where to copied files will be placed.

### Prerequisites

* Python 3.x +

### Running

After modifying the rules.json file, run the mimeo.py file.
The rules file must be in the same directory as mimeo.py and must be named "rules.json".
```
$ python mimeo.py
```

## Errors

Mimeo verifies that paths, and filenames are valid before copying files. If an original path, or backup path is not valid or does not exist for a particular rule, that rule will not be carried out. Hashs are carried out on orignal and copied files. Check the log for details.
