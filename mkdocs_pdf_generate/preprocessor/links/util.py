import os
from pathlib import Path, PosixPath, WindowsPath
import re

from weasyprint import urls
from bs4 import BeautifulSoup


# check if href is relative --
# if it is relative it *should* be an HTML that generates a PDF doc
def is_doc(href: str):
    tail = Path(href).name
    ext = Path(tail).suffix

    absurl = urls.url_is_absolute(href)
    abspath = os.path.isabs(href)
    htmlfile = ext.startswith(".html")
    relative_link = re.search(r"^\.{,2}?[\w\-.~$&+,/:;=?@%#*]*?$", href)
    if relative_link is not None:
        return True
    if absurl or abspath or not htmlfile:
        return False

    return True


# def rel_pdf_href(href: str):
#     head, tail = os.path.split(href)
#     filename, _ = os.path.splitext(tail)
#
#     internal = href.startswith("#")
#     if not is_doc(href) or internal:
#         return href
#
#     return urls.iri_to_uri(os.path.join(head, filename + ".pdf"))


def rel_html_href(base_url: str, href: str, site_url: str):
    base_url = os.path.dirname(base_url)
    rel_url = base_url.replace("file://", "")

    internal = href.startswith("#")
    web_url = re.search(r"^(https://|http://)", href)
    if web_url or internal or not is_doc(href):
        return href

    abs_html_href = Path(rel_url).joinpath(href).resolve()
    if isinstance(abs_html_href, PosixPath):
        abs_html_href = re.sub(
            r"^(/tmp|tmp)/(mkdocs|pages)[\w\-]+",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
    elif isinstance(abs_html_href, WindowsPath):
        abs_html_href = re.sub(
            r"^[\w\-:\\]+\\+(temp|Temp)\\+(mkdocs|pages)[\w\-]+",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
        abs_html_href = abs_html_href.replace("\\", "/")

    if abs_html_href:
        return urls.iri_to_uri(abs_html_href)
    return href


def abs_asset_href(href: str, base_url: str):
    if urls.url_is_absolute(href) or Path(href).is_absolute():
        return href
    return urls.iri_to_uri(urls.urljoin(base_url, href))


# makes all relative asset links absolute
def replace_asset_hrefs(soup: BeautifulSoup, base_url: str):
    for link in soup.find_all("link", href=True):
        link["href"] = abs_asset_href(link["href"], base_url)

    for asset in soup.find_all(src=True):
        asset["src"] = abs_asset_href(asset["src"], base_url)
    return soup
