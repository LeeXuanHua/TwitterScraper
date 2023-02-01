import httpx
import asyncio
import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from .utils import log_wrapper, RawConfigParser

'''
Currently aims to retrieve realtime streams of tweets related to twitter's recent layoffs.
# TODO: Add support for other topics
'''

class TwitterStream:
    # Define thread function
    @staticmethod
    @log_wrapper
    def create_thread(bearer_token: str, config: RawConfigParser, logger: logging.Logger, formatter: logging.Formatter) -> None:
        '''
        Creates a thread to:
        1. Create a logger object
        2. Initialise a TwitterStream class
        3. Run the main function of the class asynchronously
        4. Handles all errors from this object
        '''
        logger_file_handler = RotatingFileHandler(
            config["FILEPATHS"]["stream_tweet_log_file"],
            mode='a',
            maxBytes=1024 * 1024,
            backupCount=100,
            encoding="utf8",
        )
        logger_file_handler.setLevel(logging.INFO)
        logger_file_handler.setFormatter(formatter)

        stream_logger = logging.getLogger(f"{__name__}.stream_tweets")  # Initialise Parent-Child logger relationship
        stream_logger.propagate = True  # By default, propagate is True
        stream_logger.setLevel(logging.INFO)
        stream_logger.addHandler(logger_file_handler)

        while True:
            try:
                twitter_stream = TwitterStream(bearer_token, config, stream_logger)
                asyncio.run(twitter_stream.main())
                break

            except httpx.RequestError as e:   # Handle request errors
                logger.error(f"Stream Tweet Failed - {e}")
                logger.error(f"Retrying Stream Tweet")
            
            except httpx.HTTPStatusError as e:   # Handle response errors
                # If rate limit has been reached, wait until reset time
                if e.response.status_code == 429:
                    logger.error(f"Rate limit reached, waiting until reset time: {e.response.headers['x-rate-limit-reset']}")
                    time.sleep(int(e.response.headers["x-rate-limit-reset"]) - time.time())
                logger.error(f"Stream Tweet Failed - {e}")
                logger.error(f"Retrying Stream Tweet")

            except Exception as e:
                logger.error(f"Stream Tweet Failed - {e}")
                break

    def __init__(self, bearer_token: str, config: RawConfigParser, logger: logging.Logger):
        self.bearer_token = bearer_token
        self.config = config
        self.logger = logger
    
    async def main(self) -> None:
        '''
        Performs the following in sequence:
        1. Get all stream rules for user's twitter account
        2. Delete all stream rules for user's twitter account
        3. Set new stream rules for user's twitter account
        4. Get stream of tweets based on the new stream rules
        '''
        rules = await self.get_rules()
        delete = await self.delete_all_rules(rules)
        set = await self.set_rules(delete)
        await self.get_stream(set)

    def bearer_oauth(self, r: httpx.AsyncClient) -> httpx.AsyncClient:
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r


    async def get_rules(self) -> dict:
        session = httpx.AsyncClient(timeout=30)
        response = await session.get(self.config["LINKS"]["twitter_stream_rules_link"], auth=self.bearer_oauth)
        await session.aclose()

        if response.status_code != 200:
            raise httpx.HTTPStatusError(f"Cannot get rules (HTTP {response.status_code}): {response.text}",
                request=response.request,
                response=response)
        self.logger.info(f"Get Rules: {json.dumps(response.json(), sort_keys=True)}")
        return response.json()


    async def delete_all_rules(self, rules) -> None:
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}

        session = httpx.AsyncClient(timeout=30)
        response = await session.post(self.config["LINKS"]["twitter_stream_rules_link"], auth=self.bearer_oauth, json=payload)
        await session.aclose()

        if response.status_code != 200:
            raise httpx.HTTPStatusError(f"Cannot delete rules (HTTP {response.status_code}): {response.text}",
                request=response.request,
                response=response)
        self.logger.info(f"Delete All Rules: {json.dumps(response.json(), sort_keys=True)}")


    async def set_rules(self, delete) -> dict:
        rules = []

        # Deprecated - Rules are no longer stored under STREAMRULE section
        # for option in self.config.options("STREAMRULE", no_defaults=True):
        #     rules.append({"value": self.config.get('STREAMRULE', option)})
        # config_rule = ast.literal_eval(self.config["STREAMTWEET"]["rule"])    # do not require ast.literal since data are stored in list format already
        # config_tag = ast.literal_eval(self.config["STREAMTWEET"]["tag"])      # do not require ast.literal since data are stored in list format already
        for rule, tag in zip(self.config["STREAMTWEET"]["rule"], self.config["STREAMTWEET"]["tag"]):
            rules.append({"value": rule, "tag": tag})

        payload = {"add": rules}

        session = httpx.AsyncClient(timeout=30)
        response = await session.post(self.config["LINKS"]["twitter_stream_rules_link"], auth=self.bearer_oauth, json=payload)
        await session.aclose()

        if response.status_code != 201:
            raise httpx.HTTPStatusError(f"Cannot add rules (HTTP {response.status_code}): {response.text}",
                request=response.request,
                response=response)
        self.logger.info(f"Set Rules: {json.dumps(response.json(), sort_keys=True)}")


    async def get_stream(self, set) -> None:
        session = httpx.AsyncClient(timeout=30)

        async with session.stream("GET", self.config["LINKS"]["twitter_stream_link"], auth=self.bearer_oauth) as response:
            if response.status_code != 200:
                raise httpx.HTTPStatusError(f"Cannot get stream (HTTP {response.status_code}): {response.aiter_raw()}",
                    request=response.request,
                    response=response)

            async for response_line in response.aiter_text():
                if response_line and response_line != "\r\n" and response_line != "\n":
                    json_response = json.loads(response_line)
                    self.logger.info(json.dumps(json_response, sort_keys=True))

        await session.aclose()

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
    logger_file_handler = RotatingFileHandler(
        config["FILEPATHS"]["stream_tweet_log_file"],
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