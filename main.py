import os
import sys
import logging
import threading
import logging.config
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from typing import List

from cli.twiquery_cli import TwiQueryCLI
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
    formatter = logging.Formatter("[%(asctime)s]:%(levelname)5s:%(message)s")

    logger_file_handler = RotatingFileHandler(
        "main.log",
        mode="a",
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
    

    # Initialise the CLI and parser
    arg_parser = TwiQueryCLI()

    # Parse args
    args, unknown_args = arg_parser.parse_known_args()

    # Check for errorneous input
    # ERROR:User Tweet Failed - Request returned an error: 400 {"errors":[{"parameters":{"max_results":["3"]},"message":"The `max_results` query parameter value [3] is not between 5 and 100"}],"title":"Invalid Request","detail":"One or more parameters to your request was invalid.","type":"https://api.twitter.com/2/problems/invalid-request"}
    assert (5 <= args.count <= 100), main_logger.error("Count must be between 5 and 100!")
    assert (len(args.rule) == len(args.tag)), main_logger.error("Number of rules and tags do not match!")

    # Save args to config
    if args.subcommand == None:
        # Set the options for usertweet and streamtweet
        # If use_previous is set, do not overwrite the config file. Otherwise, overwrite the config file
        if args.use_previous == False:
            config.set("USERTWEET",     "username",                 args.user)
            config.set("USERTWEET",     "count",                    args.count)

            config.set("STREAMTWEET",   "rule",                     args.rule)
            config.set("STREAMTWEET",   "tag",                      args.tag)
            config.set("STREAMTWEET",   "duration",                 args.duration)

        # Initialise all services if update_settings is not set
        for option in config.options("API", no_defaults=True):
            config.set("API", option, True) if args.update_settings == False else config.set("API", option, False)

    elif args.subcommand == "usertweet":
        # Set the options for usertweet
        # If use_previous is set, do not overwrite the config file. Otherwise, overwrite the config file
        if args.use_previous == False:
            config.set("USERTWEET",     "username",                 args.user)
            config.set("USERTWEET",     "count",                    args.count)

            config.set("USERFIELDS",    "created_at",             args.u_created_at)
            config.set("USERFIELDS",    "description",            args.u_description)
            config.set("USERFIELDS",    "entities",               args.u_entities)
            config.set("USERFIELDS",    "id",                     args.u_id)
            config.set("USERFIELDS",    "location",               args.u_location)
            config.set("USERFIELDS",    "name",                   args.u_name)
            config.set("USERFIELDS",    "pinned_tweet_id",        args.u_pinned_tweet_id)
            config.set("USERFIELDS",    "profile_image_url",      args.u_profile_image_url)
            config.set("USERFIELDS",    "protected",              args.u_protected)
            config.set("USERFIELDS",    "public_metrics",         args.u_public_metrics)
            config.set("USERFIELDS",    "url",                    args.u_url)
            config.set("USERFIELDS",    "username",               args.u_username)
            config.set("USERFIELDS",    "verified",               args.u_verified)
            config.set("USERFIELDS",    "withheld",               args.u_withheld)

            config.set("TWEETFIELDS",   "attachments",            args.t_attachments)
            config.set("TWEETFIELDS",   "author_id",              args.t_author_id)
            config.set("TWEETFIELDS",   "context_annotations",    args.t_context_annotations)
            config.set("TWEETFIELDS",   "conversation_id",        args.t_conversation_id)
            config.set("TWEETFIELDS",   "created_at",             args.t_created_at)
            config.set("TWEETFIELDS",   "entities",               args.t_entities)
            config.set("TWEETFIELDS",   "geo",                    args.t_geo)
            config.set("TWEETFIELDS",   "id",                     args.t_id)
            config.set("TWEETFIELDS",   "in_reply_to_user_id",    args.t_in_reply_to_user_id)
            config.set("TWEETFIELDS",   "lang",                   args.t_lang)
            config.set("TWEETFIELDS",   "non_public_metrics",     args.t_non_public_metrics)
            config.set("TWEETFIELDS",   "organic_metrics",        args.t_organic_metrics)
            config.set("TWEETFIELDS",   "possibly_sensitive",     args.t_possibly_sensitive)
            config.set("TWEETFIELDS",   "promoted_metrics",       args.t_promoted_metrics)
            config.set("TWEETFIELDS",   "public_metrics",         args.t_public_metrics)
            config.set("TWEETFIELDS",   "referenced_tweets",      args.t_referenced_tweets)
            config.set("TWEETFIELDS",   "source",                 args.t_source)
            config.set("TWEETFIELDS",   "text",                   args.t_text)
            config.set("TWEETFIELDS",   "withheld",               args.t_withheld)
        
        # Initialise only usertweet service if update-settings is not set
        for option in config.options("API", no_defaults=True):
            if args.update_settings == False and option == "user_tweet":
                config.set("API", option, True)
            else:
                config.set("API", option, False)

    elif args.subcommand == "streamtweet":
        # Set the options for streamtweet
        # If use_previous is set, do not overwrite the config file. Otherwise, overwrite the config file
        if args.use_previous == False:
            config.set("STREAMTWEET",   "rule",                     args.rule)
            config.set("STREAMTWEET",   "tag",                      args.tag)
            config.set("STREAMTWEET",   "duration",                 args.duration)
        
        # Initialise only streamtweet service if update-settings is not set
        for option in config.options("API", no_defaults=True):
            if args.update_settings == False and option == "stream_tweet":
                config.set("API", option, True)
            else:
                config.set("API", option, False)

    # Rewrite the config file
    with open("config.ini", "w") as f:
        config.write(f)
    main_logger.info("Settings updated successfully!")

    # If update-settings is set, exit the program
    if args.update_settings == True:
        main_logger.info("Program exiting ...")
        sys.exit(0)
    
    # Reread the config file
    config = RawConfigParser()
    config.read("config.ini")
    
    # Based on config file, initialize services per thread
    thread_list: List[threading.Thread] = []
    
    if config["API"]["user_tweet"] == "True":
        thread_list.append(threading.Thread(
            target=TwitterUser.create_thread, 
            name="UserTweetThread",
            kwargs={
                "bearer_token": bearer_token, 
                "config": config, 
                "logger": main_logger, 
                "formatter": formatter
                }))
    
    if config["API"]["stream_tweet"] == "True":
        thread_list.append(threading.Thread(
            target=TwitterStream.create_thread, 
            name="StreamTweetThread",
            kwargs={
                "bearer_token": bearer_token, 
                "config": config, 
                "logger": main_logger, 
                "formatter": formatter
                }))
        
    # Start services
    for thread in thread_list:
        thread.start()
        main_logger.info(f"{thread.getName()} started")
    
    # Wait for services to finish
    for thread in thread_list:
        thread.join()
        main_logger.info(f"{thread.getName()} joined")

    # Close logging
    main_logger.info("All threads completed")
    main_logger.info("Program shutting down ...")
    logging.shutdown()