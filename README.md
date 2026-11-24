# Sahayika / MaidMate

Flask + MySQL platform connecting households (customers) with maids, with
Admin-controlled verification, matching, assignment, attendance and payroll.

## Setup
1. `python -m venv venv` and activate it, then `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in the values.
3. Create the MySQL database and tables (the schema is not part of this
   repository yet - export it from your database with `mysqldump --no-data`
   and commit it as `schema.sql`).
4. `python scripts/create_admin.py`
5. `python run.py` (set `FLASK_DEBUG=1` only on your own machine)

## Tests
`pip install -r requirements-dev.txt` then `pytest` (no database needed).
Scripts in `tests/manual/` talk to a real database/server and are run by hand.
