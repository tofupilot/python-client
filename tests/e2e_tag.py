"""Marks every name the suites create as belonging to one CI run.

The four client suites share a single organization, so clients/e2e-cleanup.py
deletes by tag rather than by age: untagged entities are never touched, which
puts a concurrent job's data — and anything a human seeded — out of reach by
construction. The workflow sets E2E_TAG once per run.

THE BUDGET IS 60 CHARACTERS
---------------------------
Most names the API accepts are capped at 60 characters, and a name is a
literal prefix plus a fragment from here. The tag costs 10, so a fragment has
to stay at 14 for the longest prefix in the suite to fit — the worst name
lands at 57. This is why a fragment carries the tag exactly once: gluing two
of them into one name spends the tag twice and overflows the cap.

WHY A COUNTER AND NOT A UUID
----------------------------
Uniqueness has two axes, and each gets the mechanism that settles it exactly:
the tag separates CI runs, the counter separates names inside one run. Four
characters of random hex would also fit the budget, but they collide once in
a few thousand names — and a suite that fails one run in a thousand teaches
everyone to press retry instead of reading the failure. A counter cannot
collide at all.

The counter assumes the suite runs in a single process, which it does:
`python -m pytest tests/v2/`, with pytest-xdist not installed. Adding xdist
means giving each worker its own tag, not a longer counter.
"""

import itertools
import os
import string
import uuid

_ALPHABET = string.digits + string.ascii_lowercase
_counter = itertools.count()

# Local runs need a tag of their own: with a counter, a fixed "e2elocal" would
# make two runs in a row produce exactly the same names. Ten characters, so a
# fragment costs the same locally as in CI and the 60-char budget holds either
# way. Matches TAG_PATTERN in clients/e2e-cleanup.py, and the other three
# suites build theirs the same way.
_LOCAL_TAG = "e2el" + uuid.uuid4().hex[:6]


def e2e_tag() -> str:
    return os.environ.get("E2E_TAG") or _LOCAL_TAG


def _base36(n: int, width: int = 3) -> str:
    """Widens past `width` rather than wrapping: past 46 656 names a fragment
    grows by a character, which is visible, instead of repeating one, which is
    not."""
    out = ""
    while n:
        n, remainder = divmod(n, 36)
        out = _ALPHABET[remainder] + out
    return out.rjust(width, "0")


def uid() -> str:
    """A name fragment no other run — and no other name in this run — produces.

    The "p" marks the python suite. The Rust ("r"), C++ ("c") and C# ("s")
    suites build theirs identically, each with its own letter and its own
    counter: they run as four separate processes, so the letter is the only
    thing keeping two of them from handing out the same number.
    """
    return f"{e2e_tag()}p{_base36(next(_counter))}"
