# mcotp-utils
**Utilities For Managing the Music Collection of The People**

This is (or, well, might someday become) a set of utilities for managing a music collection. The aim here is to make it
easier to attain/maintain conformance with the Naming Convention of The People. That, in turn, makes it easier to
navigate, explore, analyze, and listen to the collection.

## Installation and Usage

### Immediately after you clone this repository
I recommend you set up a virtual environment for this project so that this project's dependencies don't conflict with
your system's general setup. This command will probably work for you (when run from the top-level of the repository):
```commandline
virtualenv -p $(which python3) venv
```

### Before you use/modify this repository
Every time you use/modify this repository, make sure you do it from inside the virtual environment:
```commandline
source venv/bin/activate
```


### After syncing the repository
Make sure you load in any dependencies this repository requires.
```commandline
pip install -r requirements.txt
```
