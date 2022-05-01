import argparse
import asyncio
import logging
import pathlib
import re
import sys
from typing import IO, List, Set
from urllib.error import URLError
from urllib.parse import urljoin

import aiofiles
import aiohttp
from aiohttp import ClientSession
from tqdm import tqdm


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("url_collector")
logging.getLogger("chardet.charsetprober").disabled = True

HREF_RE = re.compile(r'href="(.*?)"')


async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.
    kwargs are passed to `session.request()`.

    Parameters:
        url: str
        session: ClientSession
        **kwargs

    Returns:
        str
    """

    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)
    html = await resp.text()
    return html


async def parse(url: str, session: ClientSession, **kwargs) -> List[str]:
    """
    Find HREFs in the HTML of `url`.
    Returned HREFs are sorted alphanumerically.
    kwargs are passed to `fetch_html()`.

    Parameters:
        url: str
        session: ClientSession
        **kwargs

    Returns:
        List[str]
    """
    found = set()

    try:
        html = await fetch_html(url=url, session=session, **kwargs)
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None)
        )
        return []
    except Exception as e:
        logger.exception(
            "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        )
        return []

    for link in tqdm(HREF_RE.findall(html)):
        try:
            abslink = urljoin(url, link)
        except (URLError, ValueError):
            logger.exception("Error parsing URL: %s", link)
            pass
        found.add(abslink)
        logger.info("Found %d links for %s", len(found), url)

    return sorted(list(found))


async def write_one(file: IO, url: str, **kwargs) -> None:
    """
    Write the found HREFs from `url` to `file`.
    kwargs are passed to `parse()`.

    Parameters:
        file: IO
        url: str
        **kwargs

    Returns:
        None
    """
    res = await parse(url=url, **kwargs)

    if not res:
        return None

    async with aiofiles.open(file, "a") as f:
        for p in res:
            await f.write(f"{url}\t{p}\n")
        logger.info("Wrote results for source URL: %s", url)


async def bulk_crawl_and_write(file: IO, urls: Set[str], **kwargs) -> None:
    """
    Crawl & write concurrently to `file` for multiple `urls`.
    kwargs are passed to `write_one()`.

    Parameters:
        file: IO
        urls: Set[str]
        **kwargs

    Returns:
        None
    """

    async with ClientSession() as session:
        tasks = []
        for url in tqdm(urls):
            tasks.append(
                write_one(file=file, url=url, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)


def main(urls_file: str, output: str) -> None:
    """
    Reads file(s) containing the urls for HTML pages,
    asynchronously gets links found in the corresponding HTMLs
    and write the results to the output file.

    Parameters:
        urls_file: str
        output: str

    Returns:
        None
    """
    here = pathlib.Path(__file__).parent

    with open(here.joinpath(urls_file)) as input_file:
        urls = set(map(str.strip, input_file))

    with open(here.joinpath(output), "w") as output_file:
        output_file.write("source_url\tparsed_url\n")

    asyncio.run(bulk_crawl_and_write(file=here.joinpath(output), urls=urls))


if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

    parser = argparse.ArgumentParser(
        prog="url_collector",
        description="Asynchronously get links found in multiple HTML pages."
    )

    parser.add_argument(
        "-u", "--urls", required=True,
        help="Path to the file containing the urls"
        " for HTML pages separated by line break"
        )

    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()
    main(args.urls, args.output)
