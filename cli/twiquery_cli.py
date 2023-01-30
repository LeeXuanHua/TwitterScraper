import os
import argparse
import sys

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
        TwiQueryCLI.__add_usertweet_options(g)
        TwiQueryCLI.__add_streamtweet_options(g)

        # Add the version argument
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")


    @staticmethod
    def __add_subparsers(parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(
            title='Execute Single Actions',
            description='Execute a single action with the following subcommands'
            )

        usertweet_parser = subparsers.add_parser("usertweet", help="customise with username [-u], tweet count [-c], and many more")
        TwiQueryCLI.__add_usertweet_options(usertweet_parser)       # Add generic user tweet options
        TwiQueryCLI.__add_usertweetfield_options(usertweet_parser)            # Add custom user tweet fields

        streamtweet_parser = subparsers.add_parser("streamtweet", help="customise with rules [-r], timeout duration [-t] and many more")
        TwiQueryCLI.__add_streamtweet_options(streamtweet_parser)   # Add generic stream tweet options
        TwiQueryCLI.__add_streamtweetfield_options(streamtweet_parser)          # Add custom stream tweet fields


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
    def __add_usertweetfield_options(parser: argparse.ArgumentParser):
        # for "store_false", stores False when the option is specified and stores True otherwise
        parser.add_argument("--created_at",         action="store_false",     help="Remove the created_at field")
        parser.add_argument("--description",        action="store_false",     help="Remove the description field")
        parser.add_argument("--entities",           action="store_false",     help="Remove the entities field")
        parser.add_argument("--id",                 action="store_false",     help="Remove the id field")
        parser.add_argument("--location",           action="store_false",     help="Remove the location field")
        parser.add_argument("--name",               action="store_false",     help="Remove the name field")
        parser.add_argument("--pinned_tweet_id",    action="store_false",     help="Remove the pinned_tweet_id field")
        parser.add_argument("--profile_image_url",  action="store_false",     help="Remove the profile_image_url field")
        parser.add_argument("--protected",          action="store_false",     help="Remove the protected field")
        parser.add_argument("--public_metrics",     action="store_false",     help="Remove the public_metrics field")
        parser.add_argument("--url",                action="store_false",     help="Remove the url field")
        parser.add_argument("--username",           action="store_false",     help="Remove the username field")
        parser.add_argument("--verified",           action="store_false",     help="Remove the verified field")
        parser.add_argument("--withheld",           action="store_false",     help="Remove the withheld field")


    @staticmethod
    def __add_streamtweet_options(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-r",
            "--rule",
            action="store",
            metavar="rule",
            nargs=1,                                        # 1 rule
            type=str,
            default="(#OneTeam OR #LoveWhereYouWorked) -is:retweet -is:reply -is:quote -is:nullcast",
            help="",
        )
        parser.add_argument(
            "-t",
            "--timeout",
            action="store",
            metavar="XmYs",                                 # specify format
            nargs=1,                                        # 1 duration
            type=str,
            default=-1,
            help="Duration to stream tweets for, in the format of X minutes and Y seconds. Default -1 for indefinite",
        )


    @staticmethod
    def __add_streamtweetfield_options(parser: argparse.ArgumentParser):
        # for "store_false", stores False when the option is specified and stores True otherwise
        parser.add_argument("--attachments",            action="store_false",       help="Remove the attachments field")
        parser.add_argument("--author_id",              action="store_false",       help="Remove the author_id field")
        parser.add_argument("--context_annotations",    action="store_false",       help="Remove the context_annotations field")
        parser.add_argument("--conversation_id",        action="store_false",       help="Remove the conversation_id field")
        parser.add_argument("--created_at",             action="store_false",       help="Remove the created_at field")
        parser.add_argument("--entities",               action="store_false",       help="Remove the entities field")
        parser.add_argument("--geo",                    action="store_false",       help="Remove the geo field")
        parser.add_argument("--id",                     action="store_false",       help="Remove the id field")
        parser.add_argument("--in_reply_to_user_id",    action="store_false",       help="Remove the in_reply_to_user_id field")
        parser.add_argument("--lang",                   action="store_false",       help="Remove the lang field")
        parser.add_argument("--non_public_metrics",     action="store_true",        help="Include the non_public_metrics field")
        parser.add_argument("--organic_metrics",        action="store_true",        help="Include the organic_metrics field")
        parser.add_argument("--possibly_sensitive",     action="store_false",       help="Remove the possibly_sensitive field")
        parser.add_argument("--promoted_metrics",       action="store_true",        help="Include the promoted_metrics field")
        parser.add_argument("--public_metrics",         action="store_false",       help="Remove the public_metrics field")
        parser.add_argument("--referenced_tweets",      action="store_false",       help="Remove the referenced_tweets field")
        parser.add_argument("--source",                 action="store_false",       help="Remove the source field")
        parser.add_argument("--text",                   action="store_false",       help="Remove the text field")
        parser.add_argument("--withheld",               action="store_false",       help="Remove the withheld field")


    def parse_known_args(self):
        return self.arg_parser.parse_known_args()


if __name__ == "__main__":
    # Initialise the CLI and parser
    arg_parser = TwiQueryCLI()

    ## parse args
    args, unknown_args = arg_parser.parse_known_args()
    print(args)

    sys.exit()