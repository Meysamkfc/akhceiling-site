# -*- coding: utf-8 -*-
import sqlite3
from flask import g
from config import DB_PATH
from jalali import jyear

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY,
  role TEXT NOT NULL CHECK(role IN ('customer','sales','admin')),
  name TEXT NOT NULL, company TEXT, phone TEXT UNIQUE, email TEXT UNIQUE, city TEXT, job TEXT,
  pass_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','active','rejected','disabled')),
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')), last_login TEXT,
  failed INTEGER NOT NULL DEFAULT 0, locked_until TEXT
);
CREATE TABLE IF NOT EXISTS leads(
  id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE,
  source TEXT NOT NULL CHECK(source IN ('quote','assistant','contact')),
  name TEXT NOT NULL, phone TEXT NOT NULL, company TEXT, city TEXT, building TEXT, product TEXT, area REAL, descr TEXT, extra TEXT,
  status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','contacted','follow_up','proforma','won','lost')),
  assigned_to INTEGER REFERENCES users(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')), updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  ip TEXT
);
CREATE INDEX IF NOT EXISTS ix_leads_status ON leads(status, created_at);
CREATE INDEX IF NOT EXISTS ix_leads_phone ON leads(phone);
CREATE TABLE IF NOT EXISTS orders(
  id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE,
  customer_id INTEGER NOT NULL REFERENCES users(id),
  status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','reviewing','proforma_sent','confirmed','shipped','delivered','canceled')),
  city TEXT, address TEXT, desired_date TEXT, note TEXT,
  assigned_to INTEGER REFERENCES users(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')), updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS ix_orders_customer ON orders(customer_id, created_at);
CREATE TABLE IF NOT EXISTS order_items(
  id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  item_key TEXT NOT NULL, title TEXT NOT NULL, option TEXT, qty INTEGER NOT NULL, unit TEXT
);
CREATE TABLE IF NOT EXISTS files(
  id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  uploader_id INTEGER NOT NULL REFERENCES users(id),
  side TEXT NOT NULL CHECK(side IN ('customer','staff')),
  kind TEXT NOT NULL CHECK(kind IN ('invoice','plan','proforma','other')),
  orig_name TEXT NOT NULL, stored_name TEXT NOT NULL UNIQUE, mime TEXT NOT NULL, size INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS notes(
  id INTEGER PRIMARY KEY, entity TEXT NOT NULL CHECK(entity IN ('lead','order','customer')), entity_id INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id), kind TEXT NOT NULL DEFAULT 'note', text TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS ix_notes ON notes(entity, entity_id);
CREATE TABLE IF NOT EXISTS counters(name TEXT PRIMARY KEY, val INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS pageviews(
  day TEXT NOT NULL, path TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(day, path)
);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY, user_id INTEGER, action TEXT NOT NULL, detail TEXT, ip TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
"""


def connect():
    c = sqlite3.connect(str(DB_PATH), timeout=15)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def _cols(c, t):
    return {r['name'] for r in c.execute('PRAGMA table_info(%s)' % t)}


def init_db():
    c = connect()
    c.execute('PRAGMA journal_mode=WAL')
    c.executescript(SCHEMA)
    for table, col, ddl in (('leads', 'score', 'INTEGER NOT NULL DEFAULT 0'), ('leads', 'priority', "TEXT NOT NULL DEFAULT 'cold'"), ('leads', 'why', 'TEXT'),
                            ('users', 'totp_secret', 'TEXT'), ('users', 'totp_on', 'INTEGER NOT NULL DEFAULT 0'), ('users', 'job', 'TEXT'), ('users', 'country', 'TEXT')):
        if col not in _cols(c, table):
            c.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table, col, ddl))
    c.commit()
    c.close()


def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db


def close_db(_=None):
    c = g.pop('db', None)
    if c is not None:
        c.close()


def one(sql, args=()):
    return get_db().execute(sql, args).fetchone()


def all_(sql, args=()):
    return get_db().execute(sql, args).fetchall()


def run(sql, args=()):
    c = get_db()
    cur = c.execute(sql, args)
    c.commit()
    return cur.lastrowid


def next_code(prefix):
    """e.g. Q-1405-0001 — sequential per Jalali year, atomic."""
    name = '%s-%d' % (prefix, jyear())
    c = get_db()
    c.execute('BEGIN IMMEDIATE')
    row = c.execute('SELECT val FROM counters WHERE name=?', (name,)).fetchone()
    val = (row['val'] if row else 0) + 1
    c.execute('INSERT INTO counters(name,val) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET val=excluded.val', (name, val))
    c.commit()
    return '%s-%04d' % (name, val)


def audit(user_id, action, detail='', ip=''):
    run('INSERT INTO audit(user_id,action,detail,ip) VALUES(?,?,?,?)', (user_id, action, detail[:500], ip))
