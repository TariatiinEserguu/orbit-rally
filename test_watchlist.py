import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from watchlist import main


class WatchlistTest(unittest.TestCase):
    def test_requires_two_yes_votes_and_supports_changes(self):
        with TemporaryDirectory() as temp:
            db = ['--db', str(Path(temp) / 'test.sqlite3')]

            def run(*args):
                output = StringIO()
                with redirect_stdout(output):
                    result = main(db + list(args))
                return result, output.getvalue()

            self.assertEqual(run('vote', 'Arrival', '1', 'yes')[0], 1)
            self.assertEqual(run('add', 'Arrival')[0], 0)
            self.assertEqual(run('vote', 'arrival', '1', 'yes')[0], 0)
            self.assertIn('No mutual picks', run('matches')[1])
            self.assertEqual(run('vote', 'Arrival', '2', 'yes')[0], 0)
            self.assertIn('Arrival', run('matches')[1])
            self.assertEqual(run('vote', 'Arrival', '2', 'no')[0], 0)
            self.assertIn('No mutual picks', run('matches')[1])
