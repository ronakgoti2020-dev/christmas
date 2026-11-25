"""Secret Santa assignment engine.

Unrestricted draws use a cryptographically secure shuffle plus derangement
verification. Constrained draws use randomized backtracking over a bipartite
graph (givers → eligible receivers). Matching is all-or-nothing.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field


class AssignmentImpossibleError(Exception):
    def __init__(self, message: str, conflicts: list[str]):
        super().__init__(message)
        self.message = message
        self.conflicts = conflicts


@dataclass(frozen=True)
class AssignmentResult:
    mapping: dict[str, str]
    conflicts: list[str] = field(default_factory=list)


def _sattolo_cycle(ids: list[str], rng: secrets.SystemRandom) -> dict[str, str]:
    items = ids[:]
    for i in range(len(items) - 1, 0, -1):
        j = rng.randrange(i)
        items[i], items[j] = items[j], items[i]
    return {ids[i]: items[i] for i in range(len(ids))}


def unrestricted_derangement(participant_ids: list[str]) -> dict[str, str]:
    if len(participant_ids) < 2:
        raise AssignmentImpossibleError(
            "A group needs at least 2 participants before a draw can run.",
            ["minimum_participants"],
        )
    if len(set(participant_ids)) != len(participant_ids):
        raise AssignmentImpossibleError("Duplicate participant ids.", ["duplicate_participants"])

    rng = secrets.SystemRandom()
    ids = list(participant_ids)
    for _ in range(500):
        receivers = ids[:]
        rng.shuffle(receivers)
        mapping = dict(zip(ids, receivers))
        if all(giver != receiver for giver, receiver in mapping.items()):
            return mapping
    return _sattolo_cycle(ids, rng)


def _eligible_receivers(
    participant_ids: list[str],
    exclusions: dict[str, set[str]],
    locked: dict[str, str],
) -> dict[str, list[str]]:
    eligible: dict[str, list[str]] = {}
    for giver in participant_ids:
        blocked = set(exclusions.get(giver, set()))
        blocked.add(giver)
        if giver in locked:
            receiver = locked[giver]
            eligible[giver] = [receiver]
            continue
        eligible[giver] = [pid for pid in participant_ids if pid not in blocked]
    return eligible


def _conflict_report(
    participant_ids: list[str],
    eligible: dict[str, list[str]],
    locked: dict[str, str],
    names: dict[str, str] | None = None,
) -> list[str]:
    label = (lambda pid: names.get(pid, pid)) if names else (lambda pid: pid)
    conflicts: list[str] = []

    locked_receivers: dict[str, str] = {}
    for giver, receiver in locked.items():
        if giver not in participant_ids or receiver not in participant_ids:
            conflicts.append(f"Locked assignment for {label(giver)} points at someone who is not in this group.")
        if giver == receiver:
            conflicts.append(f"{label(giver)} is locked to themselves, which Secret Santa does not allow.")
        if receiver in locked_receivers:
            conflicts.append(
                f"{label(giver)} and {label(locked_receivers[receiver])} are both locked to {label(receiver)}."
            )
        locked_receivers[receiver] = giver
        if receiver not in eligible.get(giver, []):
            conflicts.append(f"{label(giver)} is locked to {label(receiver)}, but that pair is excluded.")

    for giver, receivers in eligible.items():
        if giver not in locked and not receivers:
            conflicts.append(
                f"{label(giver)} has no possible recipients after exclusions. Relax their exclusion rules."
            )

    # Hall-style tight sets of size 1 already covered; check small tight sets.
    unlocked = [g for g in participant_ids if g not in locked]
    taken = set(locked.values())
    pool = [p for p in participant_ids if p not in taken]
    for giver in unlocked:
        options = [r for r in eligible[giver] if r not in taken]
        if len(options) == 1:
            only = options[0]
            rivals = [
                g
                for g in unlocked
                if only in eligible[g] and len([r for r in eligible[g] if r not in taken]) == 1
            ]
            if len(rivals) > 1:
                names_list = ", ".join(label(g) for g in rivals)
                conflicts.append(
                    f"{names_list} can only be assigned to {label(only)}. Those constraints cannot all be satisfied."
                )

    if not conflicts:
        conflicts.append(
            "No valid complete matching exists for the current exclusion and lock rules. "
            "Remove at least one exclusion and try again."
        )
        if len(unlocked) > len(pool):
            conflicts.append("More givers remain than available recipients after locked assignments.")
    return list(dict.fromkeys(conflicts))


def constrained_matching(
    participant_ids: list[str],
    exclusions: dict[str, set[str]] | None = None,
    locked: dict[str, str] | None = None,
    names: dict[str, str] | None = None,
) -> dict[str, str]:
    if len(participant_ids) < 2:
        raise AssignmentImpossibleError(
            "A group needs at least 2 participants before a draw can run.",
            ["minimum_participants"],
        )
    exclusions = exclusions or {}
    locked = dict(locked or {})
    eligible = _eligible_receivers(participant_ids, exclusions, locked)

    rng = secrets.SystemRandom()
    mapping: dict[str, str] = dict(locked)
    taken = set(mapping.values())
    remaining = [g for g in participant_ids if g not in mapping]
    rng.shuffle(remaining)

    shuffled_options = {giver: opts[:] for giver, opts in eligible.items()}
    for opts in shuffled_options.values():
        rng.shuffle(opts)

    def backtrack(index: int) -> bool:
        if index == len(remaining):
            return True
        giver = remaining[index]
        for receiver in shuffled_options[giver]:
            if receiver in taken:
                continue
            mapping[giver] = receiver
            taken.add(receiver)
            if backtrack(index + 1):
                return True
            taken.remove(receiver)
            del mapping[giver]
        return False

    if not backtrack(0):
        raise AssignmentImpossibleError(
            "No valid Secret Santa matching exists for these constraints.",
            _conflict_report(participant_ids, eligible, locked, names),
        )

    if set(mapping.keys()) != set(participant_ids) or set(mapping.values()) != set(participant_ids):
        raise AssignmentImpossibleError(
            "Assignment engine produced an incomplete mapping.",
            ["incomplete_matching"],
        )
    if any(giver == receiver for giver, receiver in mapping.items()):
        raise AssignmentImpossibleError("Self-assignment leaked through constraints.", ["self_assignment"])
    return mapping


def draw(
    participant_ids: list[str],
    exclusions: dict[str, set[str]] | None = None,
    locked: dict[str, str] | None = None,
    names: dict[str, str] | None = None,
) -> AssignmentResult:
    exclusions = {k: set(v) for k, v in (exclusions or {}).items() if v}
    locked = locked or {}
    if not exclusions and not locked:
        mapping = unrestricted_derangement(participant_ids)
        return AssignmentResult(mapping=mapping)
    mapping = constrained_matching(participant_ids, exclusions, locked, names)
    return AssignmentResult(mapping=mapping)


def validate_mapping(mapping: dict[str, str], participant_ids: list[str]) -> None:
    ids = set(participant_ids)
    if set(mapping.keys()) != ids or set(mapping.values()) != ids:
        raise AssignmentImpossibleError("Mapping is not a perfect assignment.", ["invalid_mapping"])
    if any(g == r for g, r in mapping.items()):
        raise AssignmentImpossibleError("Self-assignment is not allowed.", ["self_assignment"])
