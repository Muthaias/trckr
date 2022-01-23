# Disclaimer
This is not the best code in the world. This is just a tribute. The goal of this project is not to create `YATTA` (Yet Another Time Tracking Application). The goal is to do some `jurassic parking` and experiment with some ideas that might have been best left unexplored. Some things are overly complicated and others might be interesting.

# Trckr
Trckr is a command line based time tracking tool or a `YATTA`. The goal with this project is to build a flexible and efficient way of tracking time spent over different projects.

The main features are as follows:
* Add annotated intervals of time
* Start and stop an annotated timer
* Get a summary of time

## Using Trckr
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
