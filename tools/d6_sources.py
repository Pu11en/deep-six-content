"""Fetch publication evidence independently of the writer; verify quoted text."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import re
import subprocess
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener


def normalized(text):
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    return " ".join(text.split()).casefold()


def source_url(url):
    p = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith("utm_")]
    return urlunsplit(("https", p.netloc.lower(), p.path.rstrip("/") or "/", urlencode(query), ""))


def allowed(url, domains):
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    return (p.scheme == "https" and not p.username and not p.password
            and p.port in (None, 443)
            and any(host == d or host.endswith("." + d) for d in domains))


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def fetch_page(url, domains):
    if not allowed(url, domains):
        raise ValueError("source_domain_not_allowed")

    class TrustedRedirects(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if not allowed(newurl, domains):
                raise ValueError("redirect_domain_not_allowed")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (DeepSix educational source check)"})
    with build_opener(TrustedRedirects()).open(req, timeout=20) as response:
        final = response.url
        body = response.read(5_000_001)
        if len(body) > 5_000_000:
            raise ValueError("source_too_large")
        if body.startswith(b"%PDF"):
            result = subprocess.run(["pdftotext", "-", "-"], input=body,
                                    capture_output=True, timeout=20)
            if result.returncode:
                raise ValueError("pdf_unreadable")
            text = result.stdout.decode("utf-8", errors="replace")
        else:
            encoding = response.headers.get_content_charset() or "utf-8"
            parser = PageText()
            parser.feed(body.decode(encoding, errors="replace"))
            text = " ".join(parser.parts)
    return text, final


def publication_key(card):
    title = re.sub(r"\W+", " ", normalized(card["title"])).strip()
    return normalized(card["publisher"]) + "|" + title


def validate_cards(cards, domains, used, legacy_log, fetcher=fetch_page):
    accepted, failures = [], []
    urls = {u for record in used for u in record["urls"]}
    pubs = {r["publication_key"] for r in used}
    lessons = {normalized(r["lesson"]) for r in used}
    digests = {r.get("page_digest") for r in used}
    legacy_urls = {source_url(u.rstrip('`).,')) for u in re.findall(r'https://[^\s)]+', legacy_log)}
    for card in cards:
        try:
            for field in ("url", "title", "publisher", "lesson", "species", "region", "limits", "date"):
                if not isinstance(card.get(field), str) or not card[field].strip():
                    raise ValueError("incomplete_source_card")
            original = source_url(card["url"])
            pub = publication_key(card)
            if original in urls | legacy_urls or pub in pubs:
                raise ValueError("publication_already_used")
            if normalized(card["lesson"]) in lessons:
                raise ValueError("lesson_already_used")
            if "b-6183" in normalized(card["title"]) or "managing household ant pests" in normalized(card["title"]):
                raise ValueError("reserved_ANT_S001")
            if not allowed(card["url"], domains):
                raise ValueError("source_domain_not_allowed")
            text, final = fetcher(card["url"], domains)
            final = source_url(final)
            digest = hashlib.sha256(normalized(text).encode()).hexdigest()
            if final in urls | legacy_urls or digest in digests:
                raise ValueError("publication_already_used")
            facts = card.get("facts", [])
            if not 1 <= len(facts) <= 4:
                raise ValueError("missing_supported_facts")
            if sum(len(f.get("quote", "").split()) for f in facts) > 25:
                raise ValueError("source_quotes_too_long")
            for fact in facts:
                if not fact.get("statement") or not fact.get("quote") or len(fact["quote"].split()) < 3:
                    raise ValueError("incomplete_fact")
                if normalized(fact["quote"]) not in normalized(text):
                    raise ValueError("quote_not_on_page")
            card = dict(card, urls=sorted({original, final}), publication_key=pub, page_digest=digest)
            accepted.append(card)
            urls.update(card["urls"])
            pubs.add(pub)
            lessons.add(normalized(card["lesson"]))
            digests.add(digest)
            if len(accepted) == 5:
                break
        except (ValueError, OSError, subprocess.SubprocessError):
            # Source failure details are deliberately text-free: no raw response
            # or provider output is persisted as a draft archive.
            failures.append({"url": card.get("url", ""), "result": "source_check_failed"})
    return accepted, failures
