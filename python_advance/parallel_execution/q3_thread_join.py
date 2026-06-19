# Q3 - Demonstrating join() method - it makes main thread wait

import threading
import time

TASK_DURATION_SECONDS: int = 2

def slow_task(name: str) -> None:
    """Simulates a task that takes a few seconds"""
    print(name, "started")
    time.sleep(TASK_DURATION_SECONDS)
    print(name, "finished")

t1 = threading.Thread(target=slow_task, args=("Task-A",))
t2 = threading.Thread(target=slow_task, args=("Task-B",))

t1.start()
t2.start()

# join() makes sure main thread waits for both to complete
t1.join()
t2.join()

# this line only prints after both threads are done
print("All tasks completed")