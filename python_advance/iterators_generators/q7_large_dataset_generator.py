# Q7 - Process large dataset using a generator (no list storage)

from typing import Iterator

TOTAL_RECORDS: int = 1_000_000

def read_large_data(total_records: int) -> Iterator[str]:
    """
    Simulates reading a huge dataset record by record.
    In real life this would read from a file or database.
    Instead of loading everything, we yield one row at a time.
    """
    for record_number in range(1, total_records + 1):
        yield "Record_" + str(record_number)

# processing 1 million records without storing all in memory
processed: int = 0
for record in read_large_data(TOTAL_RECORDS):
    # doing some work on each record
    processed += 1

print("Total records processed:", processed)