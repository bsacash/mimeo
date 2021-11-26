![mimeo](https://github.com/bsacash/mimeo/blob/master/assets/mimeo.png?raw=true)

Automate the process of backing up important files.

## Getting Started

Mimeo can copy file contents based on three different rules.
* FileRule: Backup a single file from one location to another
* FolderRule: Backup a directory or folder from one location to another
* RecentRule: Backup the N most recent files from one location to another

Modify the rules.json file to include as many rules as needed.

Examples:
```
{
  "id": "1",
  "description":"Backup the 3 most recent downloads to iCloud",
  "type":"RecentRule",
  "original_path":"/Users/Me/Downloads",
  "backup_path": "/Users/Me/iCloud/Backup/",
  "directory": "Downloads"
  "number": 3
},
{
  "id": "2",
  "type":"FileRule",
  "original_path":"/Users/Me/Desktop/notes.txt",
  "backup_path": "/Users/Me/OneDrive/Backup/Desktop",
  "directory": "Notes Text File",
  "description":"Backup 'notes.txt' to OneDrive"
},
{
  "id": "3",
  "type":"FolderRule",
  "original_path":"/Users/Me/Documents/Important",
  "backup_path": "/Users/Me/Dropbox/Backups",
  "directory": "Important"
  "description":"Backup 'Important' folder to Dropbox"
}
```

Each time a rule is carried out, a copy will be placed in a date-time folder within the named directory. The tag '[mimeo]' will be added to the directory.

### Prerequisites

* Python 3.x +

### Running

After modifying the rules.json file, run the mimeo.py file.
Pass the rules file in as an argument when running mimeo.py.
```
$ python mimeo.py
```

## Errors

Mimeo verifies that paths, and filenames are valid before copying files. If an original path, or backup path is not valid or does not exist for a particular rule, that rule will not be carried out. Hashs are carried out on orignal and copied files. Check the log for details.
