# Q5 - Two processes printing their Process IDs

from multiprocessing import Process
import os

def show_process_id(name: str) -> None:
    """Prints the name and unique process ID of this process"""
    print(name, "- Process ID:", os.getpid())

if __name__ == "__main__":
    # __main__ guard is important for multiprocessing on Windows
    p1 = Process(target=show_process_id, args=("Process-1",))
    p2 = Process(target=show_process_id, args=("Process-2",))

    p1.start()
    p2.start()

    p1.join()
    p2.join()