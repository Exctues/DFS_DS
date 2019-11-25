from utils import logger


def path_invalid(path):
    logger.handle_error(f"Path {path} is not valid!")


def path_already_exists(path):
    logger.handle_error(f"Path {path} already exists!")


def wrong_type(path, expected_type):
    # expected type = {"directory", "file"}
    if expected_type == "directory":
        real_type = "file"
    else:
        real_type = "directory"

    logger.handle_error(f"Path {path} is a {real_type}, but {expected_type} is expected.")
