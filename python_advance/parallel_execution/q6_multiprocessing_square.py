# Q6 - Calculate squares using multiprocessing Process class

from multiprocessing import Process

def print_square(num: int) -> None:
    """Calculates and prints square of a number"""
    print("Square of", num, "=", num * num)

if __name__ == "__main__":
    numbers: list[int] = [2, 3, 4, 5]
    processes: list[Process] = []

    for num in numbers:
        p = Process(target=print_square, args=(num,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()