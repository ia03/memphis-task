"""Email and phone calls to businesses."""
import argparse
import json

from _client import request


def main():
    p = argparse.ArgumentParser(description="Email and phone businesses.")
    sub = p.add_subparsers(dest="command", required=True)
    se = sub.add_parser("send_email")
    se.add_argument("--to", required=True)
    se.add_argument("--subject", required=True)
    se.add_argument("--text", required=True)
    se.add_argument("--key", required=True)
    sub.add_parser("email_inbox")
    re_ = sub.add_parser("read_email")
    re_.add_argument("message_id")
    cb = sub.add_parser("call_business")
    cb.add_argument("--number", required=True)
    cb.add_argument("--instructions", required=True)
    cb.add_argument("--key", required=True)
    cb.add_argument("--language", default="ar-EG")
    cs = sub.add_parser("call_status")
    cs.add_argument("key")
    a = p.parse_args()
    if a.command == "send_email":
        body = {"to": a.to, "subject": a.subject, "text": a.text, "key": a.key}
    elif a.command == "email_inbox":
        body = {}
    elif a.command == "read_email":
        body = {"message_id": a.message_id}
    elif a.command == "call_business":
        body = {"number": a.number, "instructions": a.instructions, "key": a.key, "language": a.language}
    else:
        body = {"key": a.key}
    print(json.dumps(request("/agent/communications/" + a.command, body), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
