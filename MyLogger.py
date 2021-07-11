import logging, coloredlogs
from re import I
from datetime import datetime

def get_formatted_logger(logger_name, level, filename, should_save=False):
    logger = logging.getLogger(logger_name)

    log_format = "%(asctime)s [%(levelname)s] %(message)s"

    FIELD_STYLES = dict(
        asctime=dict(color='green'),
        hostname=dict(color='magenta'),
        levelname=dict(color='white'),
        filename=dict(color='magenta'),
        name=dict(color='blue'),
        threadName=dict(color='green')
    )

    LEVEL_STYLES = dict(
        debug=dict(color='white'),
        info=dict(color='cyan'),
        verbose=dict(color='blue'),
        warning=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(color='red', bold=True)
    )

    coloredlogs.install(
        logger=logger,
        level=level,
        fmt=log_format,
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES,
        isatty=True
    )

    if should_save:
        formatter = coloredlogs.ColoredFormatter(
            fmt=log_format,
            level_styles=LEVEL_STYLES,
            field_styles=FIELD_STYLES,
        )
        fh = logging.FileHandler(f"{filename}.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger 