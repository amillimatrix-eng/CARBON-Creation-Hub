#!/usr/bin/env python3
"""Read-only fail-closed checks for dynamic flight register/Index continuity.

The validator never edits the register, Index, a runtime, or any schedule.
It deliberately distinguishes the latest CHECKPOINT from later LANDING/RESUME
events: a checkpoint is a recovery anchor, not necessarily the register head.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def git_blob_sha1(raw: bytes) -> str:
    """Return the Git blob object SHA-1 for exact checked-out file bytes."""
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def validate(register_bytes: bytes, index_text: str) -> list[str]:
    errors: list[str] = []
    events: list[tuple[int, dict[str, Any]]] = []
    line_by_id: dict[str, tuple[int, dict[str, Any]]] = {}
    events_by_flight: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)

    for line_no, raw_line in enumerate(register_bytes.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"register line {line_no}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(event, dict):
            errors.append(f"register line {line_no}: event must be a JSON object")
            continue

        missing = [
            key
            for key in ("event_id", "flight_id", "event_type", "status")
            if not isinstance(event.get(key), str) or not event[key].strip()
        ]
        if missing:
            errors.append(
                f"register line {line_no}: missing/invalid required field(s): "
                + ", ".join(missing)
            )
            continue

        event_id = event["event_id"]
        flight_id = event["flight_id"]
        if event_id in line_by_id:
            errors.append(
                f"register line {line_no}: duplicate event_id {event_id!r}; "
                f"first seen on line {line_by_id[event_id][0]}"
            )
        else:
            line_by_id[event_id] = (line_no, event)
        events.append((line_no, event))
        events_by_flight[flight_id].append((line_no, event))

    if not events:
        errors.append("register contains no valid events")

    launch_by_flight: dict[str, tuple[int, dict[str, Any]]] = {}
    for flight_id, flight_events in events_by_flight.items():
        launches = [
            (line_no, event)
            for line_no, event in flight_events
            if event["event_type"] == "LAUNCH"
        ]
        if len(launches) != 1:
            errors.append(
                f"flight {flight_id!r}: expected exactly one registered LAUNCH, "
                f"found {len(launches)}"
            )
            continue

        launch_by_flight[flight_id] = launches[0]
        launch_line, launch = launches[0]
        launch_auth = launch.get("authorization_id")

        for line_no, event in flight_events:
            if line_no < launch_line:
                errors.append(
                    f"flight {flight_id!r}: event {event['event_id']!r} "
                    "precedes its LAUNCH"
                )
            if line_no == launch_line:
                continue

            event_auth = event.get("authorization_id")
            # Historical rows may omit this optional field. An explicit mismatch
            # is still an integrity error and must never be silently accepted.
            if event_auth and launch_auth and event_auth != launch_auth:
                errors.append(
                    f"flight {flight_id!r}: event {event['event_id']!r} "
                    "authorization does not match its LAUNCH"
                )

            prior = event.get("prior_event")
            if prior:
                prior_record = line_by_id.get(prior)
                if prior_record is None:
                    errors.append(
                        f"register line {line_no}: prior_event {prior!r} is absent"
                    )
                else:
                    prior_line, prior_event = prior_record
                    if prior_line >= line_no:
                        errors.append(
                            f"register line {line_no}: prior_event {prior!r} "
                            "is not earlier"
                        )
                    if prior_event.get("flight_id") != flight_id:
                        errors.append(
                            f"register line {line_no}: prior_event {prior!r} "
                            "belongs to a different flight"
                        )

    # A checkpoint is a recovery anchor, so later LANDING/RESUME records can
    # follow it. The Index must reference the latest CHECKPOINT event but its blob
    # digest must cover the complete current append-only register.
    pointer = re.search(
        r"Latest continuity checkpoint(?: \([^)]*\))?:.*?event `([^`]+)`, blob `([0-9a-f]{40})`",
        index_text,
    )
    if not pointer:
        errors.append("INTAKE_INDEX.md: latest continuity checkpoint pointer not found")
    else:
        pointer_event_id, pointer_blob = pointer.groups()
        checkpoint_events = [
            (line_no, event)
            for line_no, event in events
            if event.get("event_type") == "CHECKPOINT"
        ]
        indexed = line_by_id.get(pointer_event_id)
        if indexed is None:
            errors.append(
                f"INTAKE_INDEX.md: latest checkpoint event {pointer_event_id!r} "
                "is absent from the register"
            )
        elif indexed[1].get("event_type") != "CHECKPOINT":
            errors.append(
                f"INTAKE_INDEX.md: indexed event {pointer_event_id!r} is not a CHECKPOINT"
            )
        if checkpoint_events and checkpoint_events[-1][1].get("event_id") != pointer_event_id:
            errors.append(
                "INTAKE_INDEX.md: pointer does not reference the latest CHECKPOINT "
                "event in append order"
            )
        if not checkpoint_events:
            errors.append("register contains no CHECKPOINT event for the Index anchor")

        actual_blob = git_blob_sha1(register_bytes)
        if pointer_blob != actual_blob:
            errors.append(
                "INTAKE_INDEX.md: register blob pointer is stale "
                f"(index={pointer_blob}, actual={actual_blob})"
            )

    # An Index line may call a flight "Existing flight" only if its launch is
    # registered. Historical/anomaly labels are permitted and preserve provenance.
    for line_no, line in enumerate(index_text.splitlines(), start=1):
        match = re.search(r"\*\*Existing flight:\*\*\s+`([^`]+)`", line)
        if not match:
            continue
        flight_id = match.group(1)
        if flight_id not in launch_by_flight:
            errors.append(
                f"INTAKE_INDEX.md line {line_no}: flight {flight_id!r} is labelled "
                "Existing flight but has no registered LAUNCH"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    args = parser.parse_args()

    try:
        register_bytes = args.register.read_bytes()
        index_text = args.index.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: unable to read validation inputs: {exc}")
        return 2

    errors = validate(register_bytes, index_text)
    if errors:
        print("FAIL: dynamic flight register integrity")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "PASS: JSONL structure, unique event IDs, one launch per flight, "
        "authorization consistency where recorded, prior-event ordering where linked, "
        "latest CHECKPOINT anchor, full-register Git blob hash, and Index active-flight claims."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
