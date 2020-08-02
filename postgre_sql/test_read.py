import os
import psycopg2


def get_connection():
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn)


with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('select * from races limit 1;')
        results = cur.fetchall()

print(results)
