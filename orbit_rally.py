"""A two-player arcade game about collecting fuel before time runs out."""
import math
import random
import time
import tkinter as tk
from dataclasses import dataclass

WIDTH, HEIGHT = 720, 450
ROUND_SECONDS = 45
RADIUS = 13
SPEED = 225
COLORS = ('#74f6de', '#ff8dbd')
PLAYER_KEYS = (('a', 'd', 'w', 's'), ('left', 'right', 'up', 'down'))
MOVEMENT_KEYS = {key for player in PLAYER_KEYS for key in player}


@dataclass
class Ship:
    x: float
    y: float
    score: int = 0
    shield: float = 0.0


@dataclass
class Comet:
    x: float
    y: float
    speed: float
    radius: int


def near(x, y, target_x, target_y, distance):
    return (x - target_x) ** 2 + (y - target_y) ** 2 <= distance ** 2


class Round:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.remaining = float(ROUND_SECONDS)
        self.ships = [Ship(70, HEIGHT / 2), Ship(WIDTH - 70, HEIGHT / 2)]
        self.comets = [Comet(190, 120, 125, 17), Comet(525, 190, -145, 21),
                       Comet(350, 260, 150, 16), Comet(650, 345, -170, 19)]
        self.fuel = []
        while len(self.fuel) < 7:
            self.spawn_fuel()

    def spawn_fuel(self):
        spots = [(x, y) for x in range(110, WIDTH - 88, 40)
                 for y in range(94, HEIGHT - 30, 35)
                 if all(not near(x, y, fx, fy, 38) for fx, fy in self.fuel)
                 and all(not near(x, y, ship.x, ship.y, 40) for ship in self.ships)]
        if spots:
            self.fuel.append(self.rng.choice(spots))

    def step(self, dt, keys):
        dt = min(dt, self.remaining)
        if dt <= 0:
            return
        self.remaining -= dt
        for comet in self.comets:
            comet.x = (comet.x + comet.speed * dt + 30) % (WIDTH + 60) - 30

        for ship, (left, right, up, down) in zip(self.ships, PLAYER_KEYS):
            dx = (right in keys) - (left in keys)
            dy = (down in keys) - (up in keys)
            if dx or dy:
                distance = SPEED * dt / math.hypot(dx, dy)
                ship.x = max(RADIUS, min(WIDTH - RADIUS, ship.x + dx * distance))
                ship.y = max(71, min(HEIGHT - RADIUS, ship.y + dy * distance))
            ship.shield = max(0.0, ship.shield - dt)
            if not ship.shield and any(near(ship.x, ship.y, comet.x, comet.y, RADIUS + comet.radius)
                                       for comet in self.comets):
                ship.score = max(0, ship.score - 1)
                ship.shield = 0.9

        remaining_fuel = []
        for x, y in self.fuel:
            distances = [((ship.x - x) ** 2 + (ship.y - y) ** 2, index)
                         for index, ship in enumerate(self.ships)]
            distances.sort()
            (distance, winner), (other, _) = distances
            if distance <= (RADIUS + 9) ** 2 and distance < other:
                self.ships[winner].score += 1
            else:
                remaining_fuel.append((x, y))
        replacements = len(self.fuel) - len(remaining_fuel)
        self.fuel = remaining_fuel
        for _ in range(replacements):
            self.spawn_fuel()


class OrbitRally:
    def __init__(self, root):
        self.root = root
        root.title('Orbit Rally')
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='#101426', highlightthickness=0)
        self.canvas.pack()
        self.round = Round()
        self.keys = set()
        self.running = False
        self.last_tick = time.monotonic()
        sky = random.Random(32)
        self.stars = [(sky.randrange(WIDTH), sky.randrange(65, HEIGHT), sky.choice((1, 1, 2))) for _ in range(100)]
        root.bind('<KeyPress>', self.press)
        root.bind('<KeyRelease>', lambda event: self.keys.discard(event.keysym.lower()))
        root.bind('<FocusOut>', lambda event: self.keys.clear())
        self.tick()

    def press(self, event):
        key = event.keysym.lower()
        if key == 'return' and (not self.running or self.round.remaining <= 0):
            self.round = Round()
            self.running = True
            self.last_tick = time.monotonic()
            self.keys.clear()
        elif key in MOVEMENT_KEYS:
            self.keys.add(key)

    def tick(self):
        now = time.monotonic()
        if self.running and self.round.remaining > 0:
            self.round.step(min(now - self.last_tick, 0.05), self.keys)
        self.last_tick = now
        self.draw()
        self.root.after(16, self.tick)

    def draw(self):
        c = self.canvas
        c.delete('all')
        for x, y, size in self.stars:
            c.create_oval(x, y, x + size, y + size, fill='#454867', outline='')
        c.create_rectangle(0, 0, WIDTH, 58, fill='#1b2039', outline='')
        c.create_text(23, 29, anchor='w', text=f'P1  {self.round.ships[0].score:02}', fill=COLORS[0], font=('TkDefaultFont', 16, 'bold'))
        c.create_text(WIDTH - 23, 29, anchor='e', text=f'{self.round.ships[1].score:02}  P2', fill=COLORS[1], font=('TkDefaultFont', 16, 'bold'))
        c.create_text(WIDTH / 2, 29, text=f'{math.ceil(self.round.remaining):02}s', fill='#eff0ff', font=('TkDefaultFont', 17, 'bold'))

        for comet in self.round.comets:
            x, y, r = comet.x, comet.y, comet.radius
            trail = -1 if comet.speed > 0 else 1
            c.create_polygon(x + trail * r * 3, y, x, y - r, x, y + r, fill='#60394d', outline='')
            c.create_oval(x - r, y - r, x + r, y + r, fill='#a64d55', outline='#ffad86', width=2)
            c.create_oval(x - r / 2, y - r / 3, x, y + r / 4, fill='#794151', outline='')

        for x, y in self.round.fuel:
            c.create_polygon(x, y - 10, x + 8, y, x, y + 10, x - 8, y, fill='#ffd56f', outline='#ffeba7')
        for index, ship in enumerate(self.round.ships):
            x, y = ship.x, ship.y
            if ship.shield:
                c.create_oval(x - 18, y - 18, x + 18, y + 18, outline=COLORS[index], dash=(4, 3))
            c.create_polygon(x, y - 14, x + 13, y + 11, x, y + 6, x - 13, y + 11, fill=COLORS[index])
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill='#202642', outline='')

        if not self.running:
            self.overlay('Orbit Rally', 'Collect gold fuel. Dodge the comets.', 'P1 WASD  ·  P2 Arrow keys  ·  Enter to start')
        elif self.round.remaining <= 0:
            first, second = (ship.score for ship in self.round.ships)
            winner = 'Tie game' if first == second else f'Player {1 if first > second else 2} wins'
            self.overlay(winner, f'Final score  {first} – {second}', 'Press Enter to play again')

    def overlay(self, title, subtitle, hint):
        c = self.canvas
        c.create_rectangle(126, 152, WIDTH - 126, 314, fill='#1b2039', outline='#58668e', width=2)
        for y, text, color, size in ((187, title, '#f1f2ff', 27), (229, subtitle, '#ffd56f', 13), (276, hint, '#c5cbee', 11)):
            c.create_text(WIDTH / 2, y, text=text, fill=color, font=('TkDefaultFont', size, 'bold'))


if __name__ == '__main__':
    root = tk.Tk()
    game = OrbitRally(root)
    root.mainloop()
