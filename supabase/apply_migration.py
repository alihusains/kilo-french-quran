import os
import sys
import psycopg2

if len(sys.argv) < 5:
    print("Usage: python apply_migration.py <host> <port> <dbname> <user> <password>")
    sys.exit(1)

host = sys.argv[1]
port = sys.argv[2]
dbname = sys.argv[3]
user = sys.argv[4]
password = sys.argv[5]

MIGRATION_SQL = os.path.join(os.path.dirname(__file__), "migration.sql")

with open(MIGRATION_SQL, "r") as f:
    sql = f.read()

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password,
    sslmode="require",
)
conn.autocommit = True
cur = conn.cursor()
cur.execute(sql)
cur.close()
conn.close()
print("Migration applied")
