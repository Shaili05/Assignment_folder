# Q8 - ProcessPoolExecutor for CPU-heavy parallel work

from concurrent.futures import ProcessPoolExecutor

MAX_WORKERS: int = 2

def heavy_calculation(num: int) -> int:
    """Simulates a CPU-intensive task - computing cube"""
    return num ** 3

if __name__ == "__main__":
    numbers: list[int] = [2, 4, 6, 8, 10]

    # ProcessPoolExecutor uses separate CPU cores unlike threads
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results: list[int] = list(executor.map(heavy_calculation, numbers))

    for num, result in zip(numbers, results):
        print("Cube of", num, "=", result)