# Q4 - Simulate file downloading using multiple threads

import threading
import time

SECONDS_PER_MB: float = 0.5

def download_file(file_name: str, size_mb: int) -> None:
    """
    Simulates downloading a file.
    sleep time represents the download time based on size.
    """
    print("Starting download:", file_name)
    time.sleep(size_mb * SECONDS_PER_MB)
    print("Download complete:", file_name)

files: list[tuple[str, int]] = [("report.pdf", 2), ("video.mp4", 4), ("image.png", 1)]

threads: list[threading.Thread] = []
for name, size in files:
    t = threading.Thread(target=download_file, args=(name, size))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("All downloads finished")