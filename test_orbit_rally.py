import unittest

from orbit_rally import Round, near


class RoundTests(unittest.TestCase):
    def test_seed_replays_fuel_layout_without_comet_overlap(self):
        first, second = Round(seed=42), Round(seed=42)
        self.assertEqual(first.fuel, second.fuel)
        self.assertEqual(len(first.fuel), 7)
        for x, y in first.fuel:
            self.assertFalse(any(near(x, y, comet.x, comet.y, comet.radius + 15) for comet in first.comets))

    def test_practice_starts_without_comets(self):
        self.assertEqual(Round(practice=True).comets, [])

    def test_long_frame_still_charges_the_game_clock(self):
        game = Round(seconds=30)
        game.advance(2, set())
        self.assertAlmostEqual(game.remaining, 28)

    def test_fuel_awards_a_pickup_and_a_point(self):
        game = Round(practice=True)
        ship = game.ships[0]
        game.fuel = [(ship.x, ship.y)]
        game.advance(0.02, set())
        self.assertEqual((ship.pickups, ship.score, len(game.fuel)), (1, 1, 1))


if __name__ == '__main__':
    unittest.main()
