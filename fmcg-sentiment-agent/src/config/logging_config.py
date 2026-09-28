"""
logging_config.py

Central logging setup. Call configure_logging() once, at process startup
(src/main.py for the API, src/mcp/server.py for the MCP subprocess). Every
other module just does:

    import logging
    logger = logging.getLogger(__name__)
"""

import logging
import sys


def configure_logging(level=logging.INFO, stream=None):
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=stream or sys.stdout,
        force=True,
    )
