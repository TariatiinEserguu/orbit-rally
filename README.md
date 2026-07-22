# Orbit Rally

A 2D arcade game for two players on the same keyboard. Fly through an asteroid field, collect gold fuel, and finish with the higher score.

## Play

```sh
python3 orbit_rally.py
```

Requires Python 3.10+ with Tkinter and a graphical desktop. On Debian and Ubuntu, install `python3-tk` if Tkinter is missing.

- **Player 1** moves with WASD. **Player 2** uses the arrow keys.
- Press **1**, **2**, or **3** to select a 30-, 45-, or 60-second round, then **Enter** to start or replay.
- Press **P** to pause the round and **Enter** to resume. Press **R** while paused to restart without recording a win.
- The round also pauses when you switch away from the game window.
- Each piece of fuel earns one point and respawns elsewhere.
- A comet hit costs one point and briefly shields your ship.
- Session wins carry over between rounds until you close the game. Ties count for neither player.

Press **M** between rounds to toggle comet-free practice. Practice rounds stay out of the session win count.

Run `python3 orbit_rally.py --seed 42` to replay the same starting fuel layout and compare runs.

The end-of-round summary shows each player's fuel pickups and comet hits alongside the final score and session wins.
