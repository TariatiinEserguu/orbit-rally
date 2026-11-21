# Watchlist for Two

Build a joint movie or show shortlist. Each person votes separately, and the app shows titles you both want to watch.

Requires Python 3.10 or newer. No packages to install.

```sh
python3 watchlist.py add "Arrival"
python3 watchlist.py vote "Arrival" 1 yes
python3 watchlist.py vote "Arrival" 2 yes
python3 watchlist.py matches
```

Use `list` to see every title and its current votes. Vote again to change your choice. Titles are case-insensitive. Votes are saved in `watchlist.sqlite3` in your current directory. Run both people's commands against the same local file, or specify another file with `--db path/to/watchlist.sqlite3` before the subcommand.

Run the tests with `python3 -m unittest discover`.
