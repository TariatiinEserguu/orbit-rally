"""Keep a local watchlist and find movies you both want to watch."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=Path('watchlist.sqlite3'))
    commands = parser.add_subparsers(dest='command', required=True)
    add = commands.add_parser('add')
    add.add_argument('title')
    vote = commands.add_parser('vote')
    vote.add_argument('title')
    vote.add_argument('person', choices=['1', '2'])
    vote.add_argument('choice', choices=['yes', 'no'])
    commands.add_parser('list')
    commands.add_parser('matches')
    args = parser.parse_args(argv)
    if args.command in ('add', 'vote'):
        title = args.title.strip()
        if not title:
            parser.error('title cannot be empty')
        key = title.casefold()
    with closing(sqlite3.connect(args.db)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS movies (key TEXT PRIMARY KEY, title TEXT NOT NULL, first TEXT, second TEXT)')
        if args.command == 'add':
            cursor = db.execute('INSERT OR IGNORE INTO movies (key, title) VALUES (?, ?)', (key, title))
            print(f'Added {title}' if cursor.rowcount else 'Already on the watchlist.')
        elif args.command == 'vote':
            column = {'1': 'first', '2': 'second'}[args.person]
            cursor = db.execute(f'UPDATE movies SET {column} = ? WHERE key = ?', (args.choice, key))
            if not cursor.rowcount:
                print('Add that title first.')
                return 1
            print('Vote saved.')
        else:
            query = 'SELECT title, first, second FROM movies'
            if args.command == 'matches':
                query += " WHERE first = 'yes' AND second = 'yes'"
            rows = db.execute(query + ' ORDER BY key').fetchall()
            for title, first, second in rows:
                print(f'{title} | person 1: {first or "pending"} | person 2: {second or "pending"}')
            if not rows:
                print('No mutual picks yet.' if args.command == 'matches' else 'Your watchlist is empty.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
