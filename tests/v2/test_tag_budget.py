"""Static checks on the run tag, so its two failure modes cannot come back.

Both of these were regressions this suite actually shipped, and both were found
by reading rather than by a failing test — which is why they are tests now.
Neither talks to a server: they parse the suite's own source, so they run in
milliseconds and fail on the offending line.
"""

import ast
import pathlib
import re

from ..e2e_tag import uid

SUITE = pathlib.Path(__file__).parent
# Most identifiers the V2 API accepts are capped here. Names are built as a
# literal prefix plus fragments, so this cap is a budget shared between the two.
NAME_LIMIT = 60

# Identities the purge claims by their own text, so an untagged one is either
# invisible to it forever or shared with a concurrent run:
#   - unit serial numbers key on (organization, serial) alone, and runs.create
#     upserts on that key with DO UPDATE SET revision_id — an untagged serial
#     lets a concurrent run move our unit onto its own revision, and its purge
#     then cascades ours away with it.
#   - procedures are claimed by name, so an untagged name is never deleted.
# Part and revision numbers are deliberately absent: a part is claimed on
# "number name" so its number carries the tag, and revisions are scoped to a
# part and disappear with it by cascade.
CLAIMED_BY_TEXT = {
    ("runs", "serial_number"),
    ("units", "serial_number"),
    ("procedures", "name"),
}


def _test_files() -> list[pathlib.Path]:
    return sorted(SUITE.rglob("test_*.py"))


def _lines_under_expected_failure(tree: ast.Module) -> set[int]:
    """Line numbers inside a block that asserts the call fails.

    A create that raises never inserts a row, so it cannot collide with another
    run and needs no tag.
    """
    covered: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            head = ast.dump(node.items[0].context_expr)
            if "raises" in head or "forbidden" in head.lower():
                covered.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return covered


def test_every_created_identity_carries_the_tag() -> None:
    """No successful create passes a literal where the purge reads a tag."""
    offenders: list[str] = []

    for path in _test_files():
        tree = ast.parse(path.read_text())
        excused = _lines_under_expected_failure(tree)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or node.lineno in excused:
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "create"):
                continue
            resource = getattr(func.value, "attr", None)

            for kw in node.keywords:
                if (resource, kw.arg) not in CLAIMED_BY_TEXT:
                    continue
                # A literal string cannot contain the tag: it is fixed at import
                # time, while the tag changes every run.
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    if kw.value.value.strip():
                        offenders.append(
                            f"{path.relative_to(SUITE)}:{kw.value.lineno} "
                            f"{resource}.create({kw.arg}={kw.value.value!r})"
                        )

    assert not offenders, (
        "These identities are created without the run tag, so the purge either "
        "never reclaims them or shares them with a concurrent CI run:\n  "
        + "\n  ".join(offenders)
        + "\nBuild them from uid() instead."
    )


def test_no_constructed_name_can_exceed_the_cap() -> None:
    """Every name the suite builds fits in NAME_LIMIT at the current tag length.

    The guard the docstring in e2e_tag.py describes is a character budget, and
    a budget nobody measures is a budget that gets spent: the last time it went
    over, 46 tests failed at once on names the API refused.
    """
    fragment = len(uid())
    placeholder = re.compile(r"\{[^}]*\}")
    fstring = re.compile(r'f"([^"]*)"')
    offenders: list[str] = []

    for path in _test_files():
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for template in fstring.findall(line):
                if not placeholder.search(template):
                    continue
                if not any(k in template for k in ("timestamp", "uid", "unique")):
                    continue

                length = len(placeholder.sub("", template))
                for slot in placeholder.findall(template):
                    if any(k in slot for k in ("timestamp", "uid", "unique")):
                        length += fragment
                    else:
                        length += 2  # loop index or short prefix

                if length > NAME_LIMIT:
                    offenders.append(
                        f"{path.relative_to(SUITE)}:{lineno} -> {length} chars: {template}"
                    )

    assert not offenders, (
        f"With a {fragment}-character fragment these names exceed the "
        f"{NAME_LIMIT}-character API cap:\n  " + "\n  ".join(offenders)
        + "\nShorten the literal prefix, or drop the second fragment: one "
          "fragment already makes a name unique and claimable."
    )
