## SHICoCu
_`S`emantic `H`arsh `I`nternet `Co`mment `Cu`ratory_


```json
      Since "The Algorithms" value as interaction/engagement almost any comment, mostly everyone treat them just as a metric.
  Ignoring comment contents, greenlighting anything said on them by inaction.
  And this is an issue that is going to be even worse with the rise of AI/LLM slop.
  The real value of good comments is lost.
```
```bash
      'SHICoCu' plans to provide a solution to understand what is being commented,
  and helping to curate what is allowed to stay as a comment.

      The aim is to make comments valuable again. Not by amount, but by the content on them.
  The goals are:
    * To work autonomously.
    * Moderate spam posts.
    * Fix semantically duplicated posts
    * Being able to hide or delete comments that fail to comply with a predefined ruleset.
    * Being able to archive comments.
    * Being able to flag comments to avoid it deletion.
```
```prolog
      NOTICE: NO AI OR LLMS WILL BE USED TO CREATE CODE HERE, NEITHER TO MODERATE THE COMMENTS.
```
The intention is to use "offline" NLPs (_Natural Language Processors_), while avoiding LLMs (Large Language Models). The environmental, social, economic, and content quality degradation issues brought to us by the AI bubble demerits the use of LLMs and non deterministic queries. While these being an interesting tools; queries and prompts are detrimental for this script implementation (adding processing time and hard to debug randomness/hallucinations).

## Important Notes
The main purpose of this script is to use Youtube API, but the _[daily usage quota](https://developers.google.com/youtube/v3/determine_quota_cost)_ for the API has to be taken into account while using it.
Some key info:
* You start with ``10,000`` quota units.
* Getting a list of up to ``100`` comments cost ``1`` unit.
* But inserting or modifying a comment cost ``50`` units.
* Units reset daily at midnight Pacific Time (PT)

That is why actions other than listing would be potentionaly redirected to the actual Youtube Studio pages, to save quota units.
Since there is no way to check the used quota at any given time, other than opening **Google Cloud console**, the script will only notify that it reached the quota limit once it hits a ``quotaExceeded`` error message.

## Installation Instructions

This script uses ``spaCy`` NLP models that might need to be download manually.

``python3 -m spacy download en_core_web_lg``    (probably required, almost 6gb) >>> OR JUST USE _lg INSTEAD <<<

If an error shows up due to the /tmp allocation not being big enough, this could be a workaround
``TMPDIR=/var/tmp python3 -m spacy download en_core_web_lg --no-cache-dir``

I tried using ``en_core_web__trf``instead (a larger model, around ``6GB``), but is crashes due to the use of pytorch legacy functions.

## Tentative Roadmap

Features I might include in future versions:
- Use Steam Reviews data
- Use Twitch VODs chat data
- Use videos subtitles/transcripts
- Reports automation and ``cron`` examples
- Custom NLP pipes
