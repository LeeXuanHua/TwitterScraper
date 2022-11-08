import os
import asyncio
import httpx
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from src.RawConfigParser import RawConfigParser
from src.twitter_stream import TwitterStream
from src.twitter_user import TwitterUser

'''
Manages which service to run. Currently it has to be either stream data or user data
# TODO: Add support for both concurrently
# TODO: Store in database instead of log files
# TODO: Wrap as a backend using FastAPI
# TODO: React webapp for visualizing data
# TODO: UI - Add customisation for desired usernames and stream / topic filtering
'''

if __name__ == "__main__":
    # Initialize logging, config and environment variables
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s]:%(levelname)5s:%(message)s')
    
    config = RawConfigParser()
    config.read("config.ini")

    load_dotenv()
    try:
        bearer_token = os.environ["Bearer_Token"]
    except KeyError:
        logging.critical("Bearer Token not found in environment!")

    # Initialize services
    if config["API"]["stream_tweet"] == "True":
        logger_file_handler = RotatingFileHandler(
            config["DEFAULT"]["stream_tweet_log_file"],
            mode='a',
            maxBytes=1024 * 1024,
            backupCount=100,
            encoding="utf8",
        )
        logger_file_handler.setFormatter(formatter)
        logger.addHandler(logger_file_handler)

        while True:
            try:
                twitter_stream = TwitterStream(bearer_token, config, logger)
                asyncio.run(twitter_stream.main())
                break

            except (httpx.ProtocolError, httpx.HTTPStatusError) as e:
                logger.error(f"Stream Tweet Failed - {e}")
                logger.info(f"Retrying Stream Tweet")

            except Exception as e:
                logger.error(f"Stream Tweet Failed - {e}")
                break
        
    elif config["API"]["user_tweet"] == "True":
        logger_file_handler = RotatingFileHandler(
            config["DEFAULT"]["user_tweet_log_file"],
            mode='a',
            maxBytes=1024 * 1024,
            backupCount=100,
            encoding="utf8",
        )
        logger_file_handler.setFormatter(formatter)
        logger.addHandler(logger_file_handler)

        while True:
            try:
                twitter_user = TwitterUser(bearer_token, config, logger)
                asyncio.run(twitter_user.main())
                break

            except (httpx.ProtocolError, httpx.HTTPStatusError) as e:
                logger.error(f"User Tweet Failed - {e}")
                logger.info(f"Retrying User Tweet")

            except Exception as e:
                logger.error(f"User Tweet Failed - {e}")
                break