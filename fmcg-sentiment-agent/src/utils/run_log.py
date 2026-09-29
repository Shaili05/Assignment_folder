"""
run_log.py

Shared logging helper. Every pipeline script calls log_run() once at the
end of main(), so logs/run_log.csv fills up with a real record of every
run: when it ran, what parameters were used, and what came out. This is
written by the scripts themselves as they execute, not typed up
afterward, so it's an actual record, not a summary.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

from src.config.settings import LOGS_DIR

logger = logging.getLogger(__name__)

RUN_LOG_PATH = LOGS_DIR / "run_log.csv"


def log_run(script_name, params, summary, log_path=None):
    log_path = Path(log_path or RUN_LOG_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "script", "params", "summary"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), script_name, params, summary])
    logger.info("Run logged to %s", log_path)


