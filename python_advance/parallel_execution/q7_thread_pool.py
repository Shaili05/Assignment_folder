# Q7 - ThreadPoolExecutor to run function in parallel

from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS: int = 3

def process_item(item: int) -> int:
    """Simulates processing a single item"""
    result: int = item * item
    print("Processed:", item, "-> Result:", result)
    return result

items: list[int] = [1, 2, 3, 4, 5]

# max_workers controls how many threads run at once
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    results: list[int] = list(executor.map(process_item, items))

print("All results:", results)