# Q2 - Thread that calculates sum from 1 to 100

import threading

UPPER_LIMIT: int = 100

total_sum: int = 0

def calculate_sum() -> None:
    """Adds numbers 1 to 100 and stores in global variable"""
    global total_sum
    for i in range(1, UPPER_LIMIT + 1):
        total_sum += i

sum_thread = threading.Thread(target=calculate_sum)
sum_thread.start()
sum_thread.join()  # wait for thread to finish before printing

print("Sum from 1 to", UPPER_LIMIT, ":", total_sum)