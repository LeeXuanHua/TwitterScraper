import os
import logging
import threading
import logging.config
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from typing import List

from src.utils import RawConfigParser
from src.twitter_stream import TwitterStream
from src.twitter_user import TwitterUser

'''
Manages which service to run. Currently it has to be either stream data or user data
# TODO: Add support for both concurrently (Done 3rd Dec 2022)
# TODO: Store in database instead of log files
# TODO: Wrap as a backend using FastAPI
# TODO: React webapp for visualizing data
# TODO: UI - Add customisation for desired usernames and stream / topic filtering
'''

if __name__ == "__main__":
    # Initialize logging, config and environment variables
    # Note that logging dictConfig can also be used to configure logging from a dict
    formatter = logging.Formatter('[%(asctime)s]:%(levelname)5s:%(message)s')

    logger_file_handler = RotatingFileHandler(
        "main.log",
        mode='a',
        maxBytes=1024 * 1024,
        backupCount=100,
        encoding="utf8",
    )
    logger_file_handler.setLevel(logging.WARNING)   # To handle original & (mainly) propagated logs
    logger_file_handler.setFormatter(formatter)

    main_logger = logging.getLogger(__name__)
    main_logger.setLevel(logging.WARNING)   # To handle original logs
    main_logger.addHandler(logger_file_handler)
    
    config = RawConfigParser()
    config.read("config.ini")

    load_dotenv()
    try:
        bearer_token = os.environ["Bearer_Token"]
    except KeyError:
        main_logger.critical("Bearer Token not found in environment!")  # Avoid using logging (which uses root log)
    
    # Initialize services per thread
    thread_list: List[threading.Thread] = []
    
    if config["API"]["user_tweet"] == "True":
        thread_list.append(threading.Thread(
            target=TwitterUser.create_thread, 
            kwargs={
                "bearer_token": bearer_token, 
                "config": config, 
                "logger": main_logger, 
                "formatter": formatter
                }))
    
    if config["API"]["stream_tweet"] == "True":
        thread_list.append(threading.Thread(
            target=TwitterStream.create_thread, 
            kwargs={
                "bearer_token": bearer_token, 
                "config": config, 
                "logger": main_logger, 
                "formatter": formatter
                }))
        
    # Start services
    for thread in thread_list:
        thread.start()
    
    # Wait for services to finish
    for thread in thread_list:
        thread.join()

    # Close logging
    logging.shutdown()
