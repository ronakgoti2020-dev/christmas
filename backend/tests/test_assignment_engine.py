import pytest

from app.services.assignment import AssignmentImpossibleError, draw, unrestricted_derangement, validate_mapping


def test_two_person_assignment():
    mapping = unrestricted_derangement(["a", "b"])
    assert mapping == {"a": "b", "b": "a"} or mapping == {"a": "b", "b": "a"}
    validate_mapping(mapping, ["a", "b"])
    assert mapping["a"] == "b"
    assert mapping["b"] == "a"


def test_no_self_assignment_large_group():
    ids = [str(i) for i in range(50)]
    mapping = unrestricted_derangement(ids)
    validate_mapping(mapping, ids)
    assert all(giver != receiver for giver, receiver in mapping.items())
    assert sorted(mapping.values()) == sorted(ids)


def test_every_participant_gives_and_receives_exactly_once():
    ids = [f"p{i}" for i in range(12)]
    mapping = draw(ids).mapping
    assert len(mapping) == 12
    assert len(set(mapping.values())) == 12
    assert set(mapping) == set(ids)


def test_exclusion_constraints():
    ids = ["rahul", "priya", "amit", "neha"]
    exclusions = {"rahul": {"priya"}, "priya": {"rahul"}}
    mapping = draw(ids, exclusions=exclusions).mapping
    assert mapping["rahul"] != "priya"
    assert mapping["priya"] != "rahul"
    validate_mapping(mapping, ids)


def test_impossible_mutual_exclusion_two_people():
    with pytest.raises(AssignmentImpossibleError) as exc:
        draw(["a", "b"], exclusions={"a": {"b"}, "b": {"a"}})
    assert exc.value.conflicts


def test_locked_assignment_respected():
    ids = ["a", "b", "c"]
    mapping = draw(ids, locked={"a": "c"}).mapping
    assert mapping["a"] == "c"
    validate_mapping(mapping, ids)


def test_too_few_participants():
    with pytest.raises(AssignmentImpossibleError):
        unrestricted_derangement(["only-one"])
