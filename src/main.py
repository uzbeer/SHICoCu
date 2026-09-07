# Python 3.13.7
##################
# Modules:
#
from lib.utils import *         # internal library
import argparse, asyncio, os, time    # standard
#
# from dotenv import load_dotenv  # ext: python-dotenv
# (https://github.com/theskumar/python-dotenv)
load_dotenv = extmodule("dotenv", "load_dotenv")
#
# import polars as pl             # ext: polars
pl = extmodule("polars")        # ext: polars
import datetime as dt           # standard
#
# import spacy                    # ext: asent
spacy = extmodule("spacy")
# import asent                    # ext: asent
asent = extmodule("asent")
#
# import googleapiclient.discovery  # ext: youtube
yt_builder = extmodule("googleapiclient.discovery", "build")

#################################
# Globals

yt_api_key = None
youtube = None

async def __init_yt() -> str:
    global yt_api_key
    global youtube

    load_dotenv("yt.env")
    await asyncio.sleep(2)

    yt_api_key = os.environ.get("YOUTUBE_API_KEY")
    # DEBUG TBD print(len(yt_api_key))
    youtube = yt_builder("youtube", "v3", developerKey=yt_api_key)


def welcome_msg(): # Print intro
    ora2("Welcome to ")
    bold()
    ora("SHICoCu")
    rst()
    pur(" (")
    ora2("Semantic Harsh Internet Comments Curatory")
    pur(")")
    rst("\n")

    ita()
    pur("Initializing:")
    blink()
    pur("...")
    rst(flush=True)

    time.sleep(2)

    cy("\b\b\b\a Done!                ")
    rst("\n\n")

def main():
    # commands
    #     --version
    #     get-yt   = Download comments
    #   --load  = Load comments for tests
    #   default = Help text
    parser = argparse.ArgumentParser(add_help=False,
        prog="SHICoCu",
        description="\033[1m\033[38;5;208mSHICoCu\033[0m - Semantic Harsh Internet Comment Curatory",
        epilog="\033[3mFor more info check\033[23m: https://github.com/uzbeer/SHICoCu")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable descriptive mode")

    subparsers = parser.add_subparsers(dest="command", help="Available commands:")

    version_parser = subparsers.add_parser("version", help="Return script version")

    get_yt_parser = subparsers.add_parser("get-yt", parents=[parser], help="Return script version")
    get_yt_parser.add_argument("video-id", type=str, help="Video id to fetch the comments from")
    get_yt_parser.add_argument('--limit', type=int, help="Limit results to the first n comments")

    load_parser = subparsers.add_parser("load", parents=[parser], help="Load pre downloaded list of comments")
    load_parser.add_argument("file", type=str, help="File name (without the .parquet extension)")
    load_parser.add_argument('--limit', type=int, help="Limit results to the first n comments")


    args = parser.parse_args()
    #args = subparsers.parse_args()
    # pur(args, "\n")

    match(args.command):
        case "version":
            load_dotenv()
            cy("SHICoCu version: ")
            rst()
            print(os.environ.get("SHICOCU_VERSION"))
            if (args.verbose):
                ora2("You should check for updates here: https://github.com/uzbeer/SHICoCu\n")

        case "get-yt":
            welcome_msg() # Prints the welcome text and initialize variables

            comments = []
            next_page = None
            asyncio.run(__init_yt())
            video_id = getattr(args,"video-id") # args.video-id

            if (args.verbose):
                ora2(f"Collecting comments for video[id={video_id}]:\n")

            while video_id:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=next_page,
                )
                response = request.execute()

                if (args.verbose):
                    ora2(f"Handling {len(response.get("items", []))} items.")

                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append(
                        {
                            "comment_id": item["id"],
                            "author": comment["authorDisplayName"],
                            "author_url": comment["authorChannelUrl"],
                            "viewerRating": comment["viewerRating"],
                            "likeCount": comment["likeCount"],
                            "text": comment["textDisplay"],
                            "original": comment["textOriginal"],
                            "publishedAt": comment["publishedAt"],
                            "updatedAt": comment["updatedAt"],
                        }
                    )

                next_page = response.get("nextPageToken")
                if not next_page:
                    break

            if (args.verbose):
                ora2(f"Saving comments as a dataframe.")

            df = pl.from_dicts(comments)
            cy(df.head(5))

            df.write_parquet(f"./data/{video_id}.parquet")

        case "load":
            if (args.verbose):
                ora2(f"Opening {args.file}.parquet")

            df = pl.read_parquet(f"{args.file}.parquet")
            cy(df.head(5))

        case _:
            parser.print_help()



    if False:
        # load spacy pipeline
        nlp = spacy.blank('en')
        nlp.add_pipe('sentencizer')

        # add the rule-based sentiment model
        nlp.add_pipe('asent_en_v1')

        # try an example
        texts = ['I am not very happy, but I am also not especially sad',
            'Oh great, another delay. Truly groundbreaking service.',
            'Is anyone else getting error code 404 on step 3?',
            'He went from preventing crime with glitter bombs to commiting crime with baby monitors 😭',
            'The 2024 tax reform alters capital gains rates under Section 1031 exchanges, impacting short-term real estate yields.',
            'I love baking bread. Stock markets crashed yesterday due to inflation.',]
        for t in texts:
            doc = nlp(t)

            # print polarity of document, scaled to be between -1, and 1
            pur(f"\n{t}\n")
            rst()
            # print(doc._.polarity)
            # neg=0.0 neu=0.631 pos=0.369 compound=0.7526
            p = doc._.polarity
            # print(type(p))    # DocPolarityOutput
            print(p, " >> ", sarcasm_risk(p))


    # Naturally, a simple score can be quite unsatisfying, thus Asent implements a series of visualizer to interpret the results:
    # asent.visualize(doc, style='prediction')
    # or
    # asent.visualize(doc[:5], style='analysis')


def sarcasm_risk(scores):
    compound = scores.compound
    pos = scores.positive
    neg = scores.negative #["neg"]

    # Strongly positive sentiment with negative cues may be suspicious
    positive_negative_mix = compound > 0.3 and neg > 0.15

    # Strongly negative sentiment with positive cues may be suspicious
    negative_positive_mix = compound < -0.3 and pos > 0.15

    # Very positive or negative wording can be sarcastic in some contexts
    exaggerated_sentiment = abs(compound) > 0.8

    if positive_negative_mix or negative_positive_mix:
        return "possible sarcasm"

    if exaggerated_sentiment:
        return "sarcasm possible; inspect context"

    return "probably literal"


main()
