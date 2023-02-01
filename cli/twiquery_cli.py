import argparse

VERSION = "0.0.1"

class TwiQueryCLI:
    def __init__(self) -> None:
        """
        Initialise the CLI with the following functions:
        1. Generic options for Executing Both User Tweets & Stream Tweets
        2. Subparser for User Tweets with more options
        3. Subparser for Stream Tweets with more options
        
        Generic Options for User Tweets: custom username, number of tweets
        Generic Options for Stream Tweets: custom rules, timeout duration
        """
        ## Create the parser
        self.arg_parser = argparse.ArgumentParser(
            prog='twiquery',
            usage='%(prog)s [options]',
            description='Customisable queries to Twitter API by username, rules, fields for User Tweets and/or Stream Tweets',
            epilog='This executes both user tweets and stream tweets. To execute only one, please use the subparsers {usertweet, streamtweet}',
            prefix_chars='-',
            add_help=True,
            allow_abbrev=False,
            fromfile_prefix_chars=None,
            argument_default=None,
            conflict_handler='error',
            formatter_class=argparse.RawTextHelpFormatter,
            exit_on_error=True
        )
        
        # Add the arguments - to execute both user and stream tweets
        TwiQueryCLI.__add_options(self.arg_parser)
        
        # Add the subparsers - to execute either user or stream tweets
        TwiQueryCLI.__add_subparsers(self.arg_parser)


    @staticmethod
    def __add_options(parser: argparse.ArgumentParser):
        g = parser.add_argument_group('Execute All Actions')
        TwiQueryCLI.__add_usertweet_options(g)                                  # Add generic user tweet options
        TwiQueryCLI.__add_streamtweet_options(g)                                # Add generic stream tweet options
        TwiQueryCLI.__add_misc_option(g)                                        # Add use previous and update settings option

        # Add the version argument
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")


    @staticmethod
    def __add_subparsers(parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(
            title='Execute Single Actions',
            description='Execute a single action with the following subcommands',
            dest='subcommand'                       # To know which subcommand is executed (e.g. None, usertweet, streamtweet)
            )

        usertweet_parser = subparsers.add_parser("usertweet", help="customise with username [-u], tweet count [-c], and many more")
        TwiQueryCLI.__add_usertweet_options(usertweet_parser)                   # Add generic user tweet options
        TwiQueryCLI.__add_usertweetfield_options_userquery(usertweet_parser)    # Add custom user tweet fields for querying user
        TwiQueryCLI.__add_usertweetfield_options_tweetquery(usertweet_parser)   # Add custom user tweet fields for querying tweets
        TwiQueryCLI.__add_misc_option(usertweet_parser)                         # Add use previous and update settings option

        streamtweet_parser = subparsers.add_parser("streamtweet", help="customise with rules [-r], timeout duration [-t] and many more")
        TwiQueryCLI.__add_streamtweet_options(streamtweet_parser)               # Add generic stream tweet options
        TwiQueryCLI.__add_misc_option(streamtweet_parser)                       # Add use previous and update settings option


    @staticmethod
    def __add_usertweet_options(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-u",
            "--user",
            action="store",
            metavar="x",
            nargs="+",                                      # 1 or more usernames
            type=str,
            default=["elonmusk", "realDonaldTrump"],
            help="Query the tweets for these user(s)",
        )
        parser.add_argument(
            "-c",
            "--count",
            action="store",
            metavar="x",
            nargs=1,                                        # 1 number
            type=int,
            default=5,
            help="Number of tweets to query for each username",
        )


    @staticmethod
    def __add_usertweetfield_options_userquery(parser: argparse.ArgumentParser):
        # for "store_false", stores False when the option is specified and stores True otherwise
        parser.add_argument("--u_created_at",         action="store_false",     help="(User query) Remove the created_at field")
        parser.add_argument("--u_description",        action="store_false",     help="(User query) Remove the description field")
        parser.add_argument("--u_entities",           action="store_false",     help="(User query) Remove the entities field")
        parser.add_argument("--u_id",                 action="store_false",     help="(User query) Remove the id field")
        parser.add_argument("--u_location",           action="store_false",     help="(User query) Remove the location field")
        parser.add_argument("--u_name",               action="store_false",     help="(User query) Remove the name field")
        parser.add_argument("--u_pinned_tweet_id",    action="store_false",     help="(User query) Remove the pinned_tweet_id field")
        parser.add_argument("--u_profile_image_url",  action="store_false",     help="(User query) Remove the profile_image_url field")
        parser.add_argument("--u_protected",          action="store_false",     help="(User query) Remove the protected field")
        parser.add_argument("--u_public_metrics",     action="store_false",     help="(User query) Remove the public_metrics field")
        parser.add_argument("--u_url",                action="store_false",     help="(User query) Remove the url field")
        parser.add_argument("--u_username",           action="store_false",     help="(User query) Remove the username field")
        parser.add_argument("--u_verified",           action="store_false",     help="(User query) Remove the verified field")
        parser.add_argument("--u_withheld",           action="store_false",     help="(User query) Remove the withheld field")


    @staticmethod
    def __add_usertweetfield_options_tweetquery(parser: argparse.ArgumentParser):
        # for "store_false", stores False when the option is specified and stores True otherwise
        parser.add_argument("--t_attachments",            action="store_false",       help="(Tweet query) Remove the attachments field")
        parser.add_argument("--t_author_id",              action="store_false",       help="(Tweet query) Remove the author_id field")
        parser.add_argument("--t_context_annotations",    action="store_false",       help="(Tweet query) Remove the context_annotations field")
        parser.add_argument("--t_conversation_id",        action="store_false",       help="(Tweet query) Remove the conversation_id field")
        parser.add_argument("--t_created_at",             action="store_false",       help="(Tweet query) Remove the created_at field")
        parser.add_argument("--t_entities",               action="store_false",       help="(Tweet query) Remove the entities field")
        parser.add_argument("--t_geo",                    action="store_false",       help="(Tweet query) Remove the geo field")
        parser.add_argument("--t_id",                     action="store_false",       help="(Tweet query) Remove the id field")
        parser.add_argument("--t_in_reply_to_user_id",    action="store_false",       help="(Tweet query) Remove the in_reply_to_user_id field")
        parser.add_argument("--t_lang",                   action="store_false",       help="(Tweet query) Remove the lang field")
        parser.add_argument("--t_non_public_metrics",     action="store_true",        help="(Tweet query) Include the non_public_metrics field")
        parser.add_argument("--t_organic_metrics",        action="store_true",        help="(Tweet query) Include the organic_metrics field")
        parser.add_argument("--t_possibly_sensitive",     action="store_false",       help="(Tweet query) Remove the possibly_sensitive field")
        parser.add_argument("--t_promoted_metrics",       action="store_true",        help="(Tweet query) Include the promoted_metrics field")
        parser.add_argument("--t_public_metrics",         action="store_false",       help="(Tweet query) Remove the public_metrics field")
        parser.add_argument("--t_referenced_tweets",      action="store_false",       help="(Tweet query) Remove the referenced_tweets field")
        parser.add_argument("--t_source",                 action="store_false",       help="(Tweet query) Remove the source field")
        parser.add_argument("--t_text",                   action="store_false",       help="(Tweet query) Remove the text field")
        parser.add_argument("--t_withheld",               action="store_false",       help="(Tweet query) Remove the withheld field")


    @staticmethod
    def __add_streamtweet_options(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-r",
            "--rule",
            action="store",
            metavar="rule",
            nargs="+",
            type=str,
            default=["(#OneTeam OR #LoveWhereYouWorked) -is:retweet -is:reply -is:quote -is:nullcast"],
            help="Rules to filter the Tweet stream",
        )
        parser.add_argument(
            "-t",
            "--tag",
            action="store",
            metavar="rule",
            nargs="+",
            type=str,
            default=["OneTeam & LoveWhereYouWorked"],
            help="Tags mapping to the filter rules defined in the --rule option",
        )
        parser.add_argument(
            "-d",
            "--duration",
            action="store",
            metavar="XmYs",                                 # specify format
            nargs=1,                                        # 1 duration
            type=str,
            default=-1,
            help="Duration to stream tweets for, in the format of X minutes and Y seconds. Default -1 for indefinite",
        )


    @staticmethod
    def __add_misc_option(parser: argparse.ArgumentParser):
        # Updates config.ini without executing the service - Use Case: Execute multiple services with custom options
        parser.add_argument("--update-settings",    action="store_true",      help="Set custom options in config file without executing service")

        # Ignore current options and use those specified in config file previously
        parser.add_argument("--use-previous", action="store_true", help="Use previously-set custom options in config file")


    def parse_known_args(self):
        return self.arg_parser.parse_known_args()


if __name__ == "__main__":
    # Initialise the CLI and parser
    arg_parser = TwiQueryCLI()

    # Parse args
    args, unknown_args = arg_parser.parse_known_args()
    print(args)