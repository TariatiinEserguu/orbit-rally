"""A two-player arcade game about collecting fuel before time runs out."""
import math
import random
import time
import tkinter as tk
from dataclasses import dataclass

WIDTH, HEIGHT = 720, 450
ROUND_LENGTHS = {'1': 30, '2': 45, '3': 60}
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
    heading: float = -math.pi / 2


@dataclass
class Comet:
    x: float
    y: float
    speed: float
    radius: int


def near(x, y, target_x, target_y, distance):
    return (x - target_x) ** 2 + (y - target_y) ** 2 <= distance ** 2


class Round:
    def __init__(self, seed=None, *, seconds=45):
        self.rng = random.Random(seed)
        self.remaining = float(seconds)
        self.ships = [Ship(70, HEIGHT / 2), Ship(WIDTH - 70, HEIGHT / 2)]
        self.comets = [Comet(190, 120, 125, 17), Comet(525, 190, -145, 21),
                       Comet(350, 260, 150, 16), Comet(650, 345, -170, 19)]
        self.fuel = []
        for _ in range(7):
            self.spawn_fuel()

    def spawn_fuel(self):
        spots = [(x, y) for x in range(110, WIDTH - 88, 40)
                 for y in range(94, HEIGHT - 30, 35)
                 if all(not near(x, y, fx, fy, 38) for fx, fy in self.fuel)
                 and all(not near(x, y, ship.x, ship.y, 40) for ship in self.ships)
                 and all(not near(x, y, comet.x, comet.y, comet.radius + 15)
                         for comet in self.comets)]
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
                ship.heading = math.atan2(dy, dx)
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
        self.seconds = ROUND_LENGTHS['2']
        self.round = Round(seconds=self.seconds)
        self.keys = set()
        self.running = False
        self.paused = False
        self.wins = [0, 0]
        self.last_tick = time.monotonic()
        sky = random.Random(32)
        self.stars = [(sky.randrange(WIDTH), sky.randrange(65, HEIGHT), sky.choice((1, 1, 2))) for _ in range(100)]
        root.bind('<KeyPress>', self.press)
        root.bind('<KeyRelease>', lambda event: self.keys.discard(event.keysym.lower()))
        root.bind('<FocusOut>', self.pause_round)
        self.tick()

    def pause_round(self, event=None):
        self.keys.clear()
        if self.running and self.round.remaining > 0:
            self.paused = True

    def start_round(self):
        self.round = Round(seconds=self.seconds)
        self.running = True
        self.paused = False
        self.last_tick = time.monotonic()
        self.keys.clear()

    def press(self, event):
        key = event.keysym.lower()
        between_rounds = not self.running or self.round.remaining <= 0
        if key in ROUND_LENGTHS and between_rounds:
            self.seconds = ROUND_LENGTHS[key]
            if not self.running:
                self.round.remaining = float(self.seconds)
        elif key == 'return' and between_rounds:
            self.start_round()
        elif key == 'r' and self.paused:
            self.start_round()
        elif key == 'p':
            self.pause_round()
        elif key == 'return' and self.paused:
            self.paused = False
            self.last_tick = time.monotonic()
        elif key in MOVEMENT_KEYS and not self.paused:
            self.keys.add(key)

    def tick(self):
        now = time.monotonic()
        if self.running and not self.paused and self.round.remaining > 0:
            self.round.step(min(now - self.last_tick, 0.05), self.keys)
            if self.round.remaining <= 0:
                first, second = (ship.score for ship in self.round.ships)
                if first != second:
                    self.wins[int(second > first)] += 1
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
            forward_x, forward_y = math.cos(ship.heading), math.sin(ship.heading)
            hull = [(x + forward_x * ahead - forward_y * side,
                     y + forward_y * ahead + forward_x * side)
                    for ahead, side in ((15, 0), (-11, 13), (-6, 0), (-11, -13))]
            c.create_polygon(*hull, fill=COLORS[index])
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill='#202642', outline='')

        if not self.running:
            self.overlay('Orbit Rally', 'Collect gold fuel. Dodge the comets.', f'1–3 Select {self.seconds}s  ·  Enter to start')
        elif self.paused:
            self.overlay('Paused', 'The round timer is stopped.', 'Enter to resume  ·  R to restart')
        elif self.round.remaining <= 0:
            first, second = (ship.score for ship in self.round.ships)
            winner = 'Tie game' if first == second else f'Player {1 if first > second else 2} wins'
            self.overlay(winner, f'Round  {first} – {second}     Session wins  {self.wins[0]} – {self.wins[1]}', f'1–3 Select {self.seconds}s  ·  Enter to replay')

    def overlay(self, title, subtitle, hint):
        c = self.canvas
        c.create_rectangle(126, 152, WIDTH - 126, 314, fill='#1b2039', outline='#58668e', width=2)
        for y, text, color, size in ((187, title, '#f1f2ff', 27), (229, subtitle, '#ffd56f', 13), (276, hint, '#c5cbee', 11)):
            c.create_text(WIDTH / 2, y, text=text, fill=color, font=('TkDefaultFont', size, 'bold'))


if __name__ == '__main__':
    root = tk.Tk()
    game = OrbitRally(root)
    root.mainloop()
