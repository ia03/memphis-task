"""Task 5 field coordination and durable worker inbox."""
import argparse
import json
from pathlib import Path
from urllib.parse import quote

from _client import request


def main(argv=None):
    parser = argparse.ArgumentParser(description="Task 5 field coordination and durable worker inbox.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("brief", "status", "clock"):
        sub.add_parser(name)
    inbox = sub.add_parser("inbox")
    inbox.add_argument("--after", type=int, default=0)
    message = sub.add_parser("message")
    message.add_argument("worker_id")
    message.add_argument("text")
    message.add_argument("--context-id")
    spend = sub.add_parser("spend")
    spend.add_argument("worker_id")
    spend.add_argument("amount_egp", type=int)
    spend.add_argument("purpose")
    spend.add_argument("--key", required=True)
    cancel = sub.add_parser("cancel-spend")
    cancel.add_argument("spend_id")
    review = sub.add_parser("request-review")
    review.add_argument("reason")
    sleep = sub.add_parser("sleep")
    sleep.add_argument("until_utc", help="Absolute ISO time with offset, such as 2026-10-01T13:00:00+03:00")
    photo = sub.add_parser("get-attachment")
    photo.add_argument("attachment_id")
    photo.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command in ("brief", "status", "clock"):
        result = request("/agent/" + args.command)
    elif args.command == "inbox":
        result = request("/agent/inbox", query={"after": args.after})
    elif args.command == "message":
        result = request("/agent/messages", {"worker_id": args.worker_id, "text": args.text, "context_id": args.context_id})
    elif args.command == "spend":
        result = request("/agent/spend", {"worker_id": args.worker_id, "amount_egp": args.amount_egp, "purpose": args.purpose, "idempotency_key": args.key})
    elif args.command == "cancel-spend":
        result = request("/agent/spend/" + quote(args.spend_id, safe="") + "/cancel", {})
    elif args.command == "request-review":
        result = request("/agent/request-review", {"reason": args.reason})
    elif args.command == "sleep":
        result = request("/agent/sleep", {"until_utc": args.until_utc})
    else:
        data = request("/agent/attachments/" + quote(args.attachment_id, safe=""), raw=True)
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        result = {"path": str(output), "bytes": len(data)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
