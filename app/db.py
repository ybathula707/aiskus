import sqlite3
import click
from flask import current_app, g, jsonify
from .schema import CREATE_SCHEMA_TABLE_SQL


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # For dict-like rows
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript(CREATE_SCHEMA_TABLE_SQL)
    db.commit()

    

@click.command('init-db')
def init_db_command():
    """Initialize the database tables."""
    try:
        init_db()
        click.echo('Initialized the database.')
        return jsonify({"status": "DB Init Success",
                        "message": "Successful Init of DB",
                        "error" : f"{e}"}), 200

    except Exception as e:
        return jsonify({"status": "DB failure",
                        "message": "was not able to initialize the DB",
                        "error" : f"{e}"}), 500
def init_app(app):
    app.teardown_appcontext(close_db)  # Close DB at end of request
    app.cli.add_command(init_db_command)  # Register CLI command
