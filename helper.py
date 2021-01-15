import hashlib
from pathlib import Path

def _hash_file_update(filename, hash_object):
    assert Path(filename).is_file()
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_object.update(chunk)
    return hash_object

# Get the MD5 hash of a given file
def hash_file(filename):
    return _hash_file_update(filename, hashlib.md5()).hexdigest() 

def _hash_dir_update(directory, hash_object):
    assert Path(directory).is_dir()
    for path in sorted(Path(directory).iterdir()):
        hash_object.update(path.name.encode())
        if path.is_file():
            hash_object = _hash_file_update(path, hash_object)
        elif path.is_dir():
            hash_object = _hash_dir_update(path, hash_object)
    return hash_object

# Get the MD5 hash of all the contents of a given directory
def hash_dir(directory):
    return _hash_dir_update(directory, hashlib.md5()).hexdigest() 