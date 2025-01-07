import logging

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger

def configure_logging(logger, verbosity):
    """
    Configures logging based on the verbosity level.
    :param verbosity: int, verbosity level (0=errors only, 1=info, 2=debug)
    """
    log_level = logging.ERROR  # Default level
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger.info(f"Logging configured with level: {logging.getLevelName(log_level)}")