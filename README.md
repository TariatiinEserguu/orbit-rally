# Orbit Rally

A 45-second 2D arcade game for two players on the same keyboard. Fly through an asteroid field, collect gold fuel, and finish with the higher score.

## Play

```sh
python3 orbit_rally.py
```

Requires Python 3.10+ with Tkinter and a graphical desktop. On Debian and Ubuntu, install `python3-tk` if Tkinter is missing.

- **Player 1** moves with WASD. **Player 2** uses the arrow keys.
- Press **Enter** to start or replay.
- Press **P** to pause the round and **Enter** to resume.
- Each piece of fuel earns one point and respawns elsewhere.
- A comet hit costs one point and briefly shields your ship.
