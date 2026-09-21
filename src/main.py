# Python 3.13.7
##################
# Modules:
#
from lib.utils import *         # internal library
import argparse, asyncio, os, time, unicodedata    # standard
#
# from dotenv import load_dotenv  # ext: python-dotenv
# (https://github.com/theskumar/python-dotenv)
load_dotenv = extmodule("dotenv", "load_dotenv")
#
# import polars as pl             # ext: polars
pl = extmodule("polars")
import datetime as dt           # standard
#
# import spacy                    # ext: asent
spacy = extmodule("spacy")
# import asent                    # ext: asent
asent = extmodule("asent")
#
# import googleapiclient.discovery  # ext: youtube
yt_builder = extmodule("googleapiclient.discovery", "build")


#############################
# Maybe refact all NLP libraries into it own module?
# Probably not
class NLP:
    def __init__(self, pipes: list[str] = []):
        # load spacy pipeline
        #nlp = spacy.blank('en')
        self.nlp = spacy.load('en_core_web_lg')
        for pipe in pipes:
            self.nlp.add_pipe(pipe)

    def _nlp(self, text):
        clean_text = "".join(
            c for c in text
            if unicodedata.category(c) not in ("So", "Cs")
            and not (0x200D <= ord(c) <= 0x200E or 0xFE00 <= ord(c) <= 0xFE0F)
        )
        return self.nlp(clean_text)

    def explode_polarity(self, text: str) -> dict:
        fields = self._nlp(text)._.polarity.to_dict()
        fields.pop("polarities")
        return fields

    def nonsense_estimation(self, text: str) -> float | None:
        doc = self._nlp(text)
        scores = []

        # looping sentences
        for s in doc.sents:
            subjects = [tok for tok in s if tok.dep_ == "nsubj"]
            attributes = [tok for tok in s if tok.dep_ == "attr"]

            if subjects and attributes:
                for subj in subjects:
                    if subj.pos_ != "PRON": # ignore pronouns
                        for attr in attributes:
                            if subj.has_vector and attr.has_vector:
                                scores.append(subj.similarity(attr))
        if not scores:
            return None
        return sum(scores) / len(scores)
#################################
# Globals

yt_api_key = None
youtube = None
t0 = None

def generate_cloud(df, filename: str):
    WordCloud = extmodule(wordcloud, "WordCloud")
    Counter = extmodule(collections, "Counter")
    Image =extmodule(PIL, "Image")
    ImageDraw =extmodule(PIL, "ImageDraw")
    np = extmodule(numpy)

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

    os.makedirs("./data", exist_ok=True)
    os.makedirs("./output", exist_ok=True)
    time.sleep(2)

    cy("\b\b\b\a Done!                ")
    rst("\n\n")

def main():
    par = Parser(help_text="""
\033[1m\033[38;5;208mSHICoCu\033[0m - Semantic Harsh Internet Comment Curatory

Subcommands (general):
    load_raw --file <\033[3mname\033[23m>      \033[3m Load previously downloaded data\033[23m
    load_results --file <\033[3mname\033[23m>  \033[3m Load previously displayed data\033[23m
    server [--port optional]    \033[3m Open server. Default port: 3012\033[23m
    version                     \033[3m Display script version \033[23m

Subcommands for Youtube:
    get-yt --id <\033[3mID\033[23m>      \033[3m Download root comments given a video ID\033[23m
    get-yt-held --id <\033[3mID\033[23m> \033[3m Download held comments given an owned video ID\033[23m

Subcommands for Steam:
    get-steam --id <\033[3mID\033[23m>         \033[3m Download reviews given a game ID\033[23m

Optional flags:
    --store_raw [filename]      \033[3m Keep a backup of the fetched data \033[23m
    --store_results [filename]  \033[3m Saves the processed results data \033[23m
    --cloud [filename]          \033[3m Generates word cloud from the data \033[23m
    --limit <\033[3mn\033[23m>                 \033[3m Total amount of data/rows loaded \033[23m

Concatenable flags:
    -v                          \033[3m Detailed verbose output \033[23m
    -t                          \033[3m Print processing timestamps \033[23m
    -h                          \033[3m Display help hints \033[23m

NOTES:
    Only the first subcommand is run.
    Parameters <\033[3mbetween chevrons\033[23m> are required.
    Parameters [between brackets] are optional.

\033[3mFor more info check\033[23m: https://github.com/uzbeer/SHICoCu
        \n""")

    if par("-t"):
        global t0
        t0 = timestamp(label=" Starting runtime timer\n")

    verbose = par("-v")

    token = par.tokens[0] if par.tokens else None
    match(token):
        case "version":
            load_dotenv()
            cy("SHICoCu version: ")
            rst()
            print(os.environ.get("SHICOCU_VERSION"))
            if (verbose):
                ora2("You should check for updates here: https://github.com/uzbeer/SHICoCu\n")

        case "server", "load_results", "get-yt-held":
            welcome_msg()
            print("Sorry,")
            err("         feature not implemented yet...")

        case "get-yt":
            welcome_msg() # Prints the welcome text and initialize variables

            comments = []
            next_page = None
            asyncio.run(__init_yt())
            if (par("--id")):
                video_id = par("--id")
            else:
                raise ValueError("Missing argument: --id")

            if (verbose):
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

                if (verbose):
                    ora2(f"Handling {len(response.get("items", []))} items.\n")

                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append(
                        {
                            "comment_id": item["id"],
                            "author": comment["authorDisplayName"],
                            "viewerRating": comment["viewerRating"],
                            "likeCount": comment["likeCount"],
                            "text": comment["textDisplay"],
                            "updatedAt": comment["updatedAt"],
                        }
                    )

                next_page = response.get("nextPageToken")
                if not next_page:
                    break

            df = pl.from_dicts(comments)

            if "--store_raw" in par:
                filepath = sanitize(video_id if par("--store_raw") is None else par("--store_raw"), dir="./data/", fix_dir=True, ext=".parquet")
                if (verbose):
                    ora2(f"Saving comments as a dataframe ({filepath}).\n")
                # df.write_parquet(f"./data/{video_id if par("--store_raw") is None else sanitize(par("--store_raw"))}.parquet")
                df.write_parquet(filepath)

            if (t0):
                timestamp(t0, label=f" Partial runtime ({token}) = ")

        case "load_raw":
            welcome_msg() # Prints the welcome text and initialize variables

            if (par("--file")):
                filename = sanitize(par("--file"), dir="./data/", fix_dir=True, ext=".parquet")
            else:
                raise ValueError("Missing argument: --file")

            if (verbose):
                ora2(f"Opening {filename} \n")

            df = pl.read_parquet(filename)

            if (t0):
                timestamp(t0, label=f" Partial runtime ({token}) = ")


    if (len(par.tokens) == 0):
        ora2(par.help_text)
        return


    #spaCy pipe processing
    # NOT LOAD RESULTS
    if not(df.is_empty()):
        pl.Config.set_fmt_str_lengths(340)
        pl.Config.set_tbl_formatting("UTF8_HORIZONTAL_ONLY")
        pl.Config.set_tbl_hide_column_data_types(True)
        pl.Config.set_tbl_hide_dataframe_shape(True)

        df = df.with_columns(
            pl.col("text").str.replace_all(r"[\r\n\t]", " ")
        )
        if (verbose):
            cy(df.head(5), "\n")


        ####### PROCESSING #####
        # Check if we were asked for --cloud, normal results, or to skip them
        if ("--cloud" in par.tokens) or ("--skip" in par.tokens):
            if ("--cloud" in par.tokens):
                if (verbose):
                    ora2("Starting words cloud generation...")
                generate_cloud(df, par("--cloud") or par("--id") or par("--file"))
            return
        pipes = NLP(['sentencizer', 'asent_en_v1'])

        df = df.with_columns(
            pl.col("text")
              .map_elements(pipes.explode_polarity, return_dtype=pl.Struct([
                  pl.Field("compound", pl.Float64),
                  pl.Field("negative", pl.Float64),
                  pl.Field("neutral", pl.Float64),
                  pl.Field("positive", pl.Float64)
                ]))
              .alias("to_be_exploded")
          ).unnest("to_be_exploded")
              # .str.replace_all(r"[\p{So}\x{FE0F}\x{200D}\x{2600}-\x{27BF}]", "") # before .map

        df = df.with_columns(
              pl.col("text").map_elements(
                  lambda x: pipes.nonsense_estimation(x), return_dtype=pl.Float64
                )
              .alias("nonsense_chance")
          )


        bif = Bif()
        if "--store_results" in par:
            channel = par("--store_raw") or par("--id") or par("--file")
            filepath = sanitize(channel, dir="./output/", fix_dir=True, ext=".txt")
            f = open(filepath, "w")
            if (verbose):
                ora2(f"Saving results in {filepath}\n")
            bif.add(f)

        ora("\nTop 10 positive posts\n", file=bif)
        rst(file=bif)
        print(df.sort("compound", descending=True).head(10).select([
            (
                pl.lit("Username: ") + pl.col("author").cast(pl.String) +pl.lit("\n") +
                pl.lit("Sentiment: ") + pl.col("compound").cast(pl.String) +pl.lit("\n") +
                pl.lit("Likes: ") + pl.col("likeCount").cast(pl.String) +pl.lit("\n") +
                pl.lit("ID: ") + pl.col("comment_id").cast(pl.String) + pl.lit("\n")
              ).alias("details"), pl.col("text")
          ]), file=bif)
        # print(df.sort("compound", descending=True).head(10).select("comment_id", "text", "likeCount", "compound"), file=bif)
        #                 pl.lit(": ") + pl.col().cast(pl.String) +pl.lit("\n") +


        ora("\nTop 10 negative posts\n", file=bif)
        rst(file=bif)
        print(df.sort("compound", descending=True).tail(10).select([
            (
                pl.lit("Username: ") + pl.col("author").cast(pl.String) +pl.lit("\n") +
                pl.lit("Sentiment: ") + pl.col("compound").cast(pl.String) +pl.lit("\n") +
                pl.lit("Likes: ") + pl.col("likeCount").cast(pl.String) +pl.lit("\n") +
                pl.lit("ID: ") + pl.col("comment_id").cast(pl.String) + pl.lit("\n")
              ).alias("details"), pl.col("text")
          ]), file=bif)
        # print(df.sort("compound", descending=True).tail(10).select("comment_id", "text", "likeCount", "compound"), file=bif)

        ora("\nTop 10 most likely nonsense posts\n", file=bif)
        rst(file=bif)
        print(df.sort("nonsense_chance", descending=True, nulls_last=True).head(10).select([
            (
                pl.lit("Username: ") + pl.col("author").cast(pl.String) +pl.lit("\n") +
                pl.lit("Nonsence chance: ") + pl.col("nonsense_chance").cast(pl.String) +pl.lit("\n\n") +
                pl.lit("Sentiment: ") + pl.col("compound").cast(pl.String) +pl.lit("\n") +
                pl.lit("Likes: ") + pl.col("likeCount").cast(pl.String) +pl.lit("\n") +
                pl.lit("ID: ") + pl.col("comment_id").cast(pl.String) + pl.lit("\n")
              ).alias("details"), pl.col("text")
          ]), file=bif)
        # print(df.sort("nonsense_chance", descending=True, nulls_last=True).head(10).select("comment_id", "text", "nonsense_chance", "likeCount", "compound"), file=bif)

        ora("\nTop 10 most active posters\n", file=bif)
        rst(file=bif)
        print(df.group_by("author")
            .agg(
                pl.len().alias("Total posts"),
                pl.col("compound").mean().alias("Avg compound")
            ).sort("Total posts", descending=True).head(10).select("author", "Total posts", "Avg compound"), file=bif)


main()
if (t0):
    timestamp(t0, label=" Total runtime = ")
