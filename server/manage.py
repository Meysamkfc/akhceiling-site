# -*- coding: utf-8 -*-
"""Admin CLI.   python manage.py create-user --role admin --name "..." --phone 09... [--password ...]
No default accounts exist: the first admin is created here (password is prompted for when not given)."""
import argparse
import getpass
import sys

from werkzeug.security import generate_password_hash

import db
import security as sec
from flask import Flask

app = Flask(__name__)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('create-user')
    c.add_argument('--role', choices=['admin', 'sales'], default='admin')
    c.add_argument('--name', required=True)
    c.add_argument('--phone', required=True)
    c.add_argument('--password')
    r = sub.add_parser('reset-password')
    r.add_argument('--phone', required=True)
    r.add_argument('--password')
    a = ap.parse_args()
    db.init_db()
    with app.app_context():
        phone = sec.norm_phone(a.phone)
        if not phone:
            sys.exit('شماره موبایل معتبر نیست.')
        pw = a.password or getpass.getpass('رمز عبور: ')
        err = sec.password_error(pw)
        if err:
            sys.exit(err)
        if a.cmd == 'create-user':
            if db.one('SELECT 1 FROM users WHERE phone=?', (phone,)):
                sys.exit('این شماره قبلاً ثبت شده است.')
            db.run("INSERT INTO users(role,name,phone,pass_hash,status) VALUES(?,?,?,?,'active')", (a.role, a.name, phone, generate_password_hash(pw)))
            print('کاربر ساخته شد:', a.role, phone)
        else:
            if not db.one('SELECT 1 FROM users WHERE phone=?', (phone,)):
                sys.exit('کاربری با این شماره نیست.')
            db.run('UPDATE users SET pass_hash=?, failed=0, locked_until=NULL WHERE phone=?', (generate_password_hash(pw), phone))
            print('رمز عبور تغییر کرد.')


if __name__ == '__main__':
    main()
