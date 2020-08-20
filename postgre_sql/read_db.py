import os
import psycopg2
from sqlalchemy import *
from sqlalchemy import create_engine

dsn = os.environ.get('DATABASE_URL_READONLY')
engine = create_engine(dsn)
'''
result = engine.execute("select * from races limit 10;")

for row in result:
    print(row)
'''

race_id_num = 1
q = (
  "select * from races where id <= 500;"
)

q = (
  select([
    literal_column('id'),
    literal_column('title'),
  ])
  .select_from(table('races'))
  .where(literal_column('id') >= race_id_num)
)

print(q)
result = engine.execute(q)
for row in result:
    print(row)
