# Q1 - Two threads printing numbers 1 to 5 at the same time

import threading
import time

UPPER_LIMIT: int = 5
DELAY_SECONDS: float = 0.5

def print_numbers(thread_name: str) -> None:
    """Prints 1 to 5 with a small delay to show overlap"""
    for i in range(1, UPPER_LIMIT + 1):
        print(thread_name, "->", i)
        time.sleep(DELAY_SECONDS)

thread1 = threading.Thread(target=print_numbers, args=("Thread-1",))
thread2 = threading.Thread(target=print_numbers, args=("Thread-2",))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("Both threads finished")