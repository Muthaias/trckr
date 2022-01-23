# Disclaimer
This is not the best code in the world. This is just a tribute. The goal of this project is not to create `YATTA` (Yet Another Time Tracking Application). The goal is to do some `jurassic parking` and experiment with some ideas that might have been best left unexplored. Some things are overly complicated and others might be interesting.

# Trckr
Trckr is a command line based time tracking tool or a `YATTA`. This tool wants to be a flexible and efficient way of tracking time spent over different projects. What it actually is, will be up to the users to decide.

The main features are as follows:
* Add annotated intervals of time
* Start and stop an annotated timer
* Get a summary of time

## Using Trckr
How to use Trckr is described by examples. This section includes a number of example commands and an example of a powerful repo config.

### Example commands
```sh
# Initialize trckr
# Creates a ".trckr.json" in the current directory
track init --userid <userid> --contextid <contextid>

# Start a timer from now
track start - "Work now"
# Stop a timer now
track stop -

# Start a timer from 09:00
track start 9:00 "Later morning work"
# Stop timer at specific time
track stop 16:00

# Add entry
track add 9:00 17:00 "Working 9 to 5"

# List all entries for active user in active context
track list
```

### Example config
A powerful example configurator for a project local config is as follows:
```json
{
    "data_type": "json",
    "path": "%(HOME)s/.trckr-data",
    "type": "struct",
    "userid": "%(USER)s",
    "contextid": "trckr"
}
```
Name the configuration `.trckr.json` and place it in the root of your project.

When using this config all entries and timers will be tagged with the current system user and stored in the users home directory. This allows you to commit project specific configuratons that will help structured time tracking.
