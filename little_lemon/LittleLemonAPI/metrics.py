import contextlib
from prometheus_client import Counter, Histogram
import re
import time

# Counter for the total number of database queries executed per table
db_query_count = Counter(
    'db_query_total',
    'Total number of database queries executed per table',
    ['table']
)

# Counter for the total number of records returned per table
db_records_returned = Counter(
    'db_records_returned_total',
    'Total number of records returned from queries per table',
    ['table']
)

# Histogram for query execution durations per table
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Histogram of database query durations per table',
    ['table']
    )


def get_table_name(sql):
    match = re.search(r'FROM\s+`?\"?(\w+)`?\"?', sql, re.IGNORECASE)
    return match[1] if match else 'unknown'

def database_execute_wrapper(execute, sql, params, many, context):
    start_time = time.time()

    result = execute(sql, params, many, context)

    duration = time.time() - start_time
    table_name = get_table_name(sql)

    db_query_count.labels(table=table_name).inc()
    db_query_duration.labels(table=table_name).observe(duration)

    record_count = 0
    if sql.strip().lower().startswith('select'):
        with contextlib.suppress(KeyError, TypeError):
            record_count = len(context['result'])
    db_records_returned.labels(table=table_name).inc(record_count)

    return result