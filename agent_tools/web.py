"""Web search and page reading."""
import argparse
import json

from _client import request


def main():
    p = argparse.ArgumentParser(description="Search the web and read pages.")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("query", nargs="+")
    o = sub.add_parser("open")
    o.add_argument("url")
    a = p.parse_args()
    if a.command == "search":
        out = request("/agent/web/search", query={"q": " ".join(a.query)})
    else:
        out = request("/agent/web/open", query={"url": a.url})
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
