from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from uuid import uuid4

from tests.conftest import auth_header


def _future() -> str:
    return (date.today() + timedelta(days=30)).isoformat()


def _deadline() -> str:
    return (date.today() + timedelta(days=10)).isoformat()


def test_register_and_login(client):
    headers = auth_header(client, "rahul@example.com", "Rahul")
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "rahul@example.com"
    login = client.post("/api/auth/login", json={"email": "rahul@example.com", "password": "Secret123"})
    assert login.status_code == 200
    bad = client.post("/api/auth/login", json={"email": "rahul@example.com", "password": "wrongpass1"})
    assert bad.status_code == 401


def test_unauthorized_api_access(client):
    assert client.get("/api/groups").status_code == 401
    assert client.get("/api/notifications").status_code == 401


def _create_group(client, headers, name="Christmas Friends", privacy="secret"):
    response = client.post(
        "/api/groups",
        headers=headers,
        json={
            "name": name,
            "description": "Office + friends exchange",
            "event_type": "christmas",
            "event_date": _future(),
            "registration_deadline": _deadline(),
            "minimum_budget": 20,
            "maximum_budget": 50,
            "currency": "USD",
            "country": "India",
            "exchange_type": "physical",
            "privacy_mode": privacy,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_group_creation(client):
    headers = auth_header(client, "org@example.com", "Organizer")
    group = _create_group(client, headers)
    assert group["invite_code"]
    assert "/join/" in group["invite_url"]
    listed = client.get("/api/groups", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == group["id"]


def test_join_and_duplicate_membership(client):
    organizer = auth_header(client, "org2@example.com", "Org")
    group = _create_group(client, organizer, "Family 2026")
    invite = group["invite_code"]
    guest = auth_header(client, "priya@example.com", "Priya")
    joined = client.post(
        f"/api/invitations/{invite}/join",
        headers=guest,
        json={"budget_acknowledged": True, "country": "India"},
    )
    assert joined.status_code == 201
    again = client.post(
        f"/api/invitations/{invite}/join",
        headers=guest,
        json={"budget_acknowledged": True},
    )
    assert again.status_code == 409


def test_wishlist_permissions(client):
    organizer = auth_header(client, "wish-org@example.com", "Org")
    group = _create_group(client, organizer, "Wishlist Group")
    invite = group["invite_code"]
    priya = auth_header(client, "wish-priya@example.com", "Priya")
    amit = auth_header(client, "wish-amit@example.com", "Amit")
    client.post(f"/api/invitations/{invite}/join", headers=priya, json={"budget_acknowledged": True})
    client.post(f"/api/invitations/{invite}/join", headers=amit, json={"budget_acknowledged": True})
    members = client.get(f"/api/groups/{group['id']}/participants", headers=organizer).json()
    priya_id = next(m["id"] for m in members if m["full_name"] == "Priya")
    created = client.post(
        f"/api/groups/{group['id']}/wishlist",
        headers=priya,
        json={"title": "Headphones", "category": "technology", "priority": "high", "estimated_price": 40},
    )
    assert created.status_code == 201
    forbidden = client.get(f"/api/groups/{group['id']}/wishlist", headers=amit, params={"participant_id": priya_id})
    assert forbidden.status_code == 403
    own = client.get(f"/api/groups/{group['id']}/wishlist", headers=priya)
    assert own.status_code == 200
    assert own.json()[0]["title"] == "Headphones"


def _three_member_group(client):
    suffix = uuid4().hex[:8]
    organizer = auth_header(client, f"draw-org-{suffix}@example.com", "Rahul")
    group = _create_group(client, organizer, "Draw Group")
    invite = group["invite_code"]
    priya = auth_header(client, f"draw-priya-{suffix}@example.com", "Priya")
    amit = auth_header(client, f"draw-amit-{suffix}@example.com", "Amit")
    client.post(f"/api/invitations/{invite}/join", headers=priya, json={"budget_acknowledged": True})
    client.post(f"/api/invitations/{invite}/join", headers=amit, json={"budget_acknowledged": True})
    return group, organizer, priya, amit


def test_two_person_api_assignment(client):
    organizer = auth_header(client, "pair-org@example.com", "Rahul")
    group = _create_group(client, organizer, "Pair Group")
    priya = auth_header(client, "pair-priya@example.com", "Priya")
    client.post(f"/api/invitations/{group['invite_code']}/join", headers=priya, json={"budget_acknowledged": True})
    drawn = client.post(f"/api/groups/{group['id']}/assignments/draw", headers=organizer)
    assert drawn.status_code == 200
    mine = client.get(f"/api/groups/{group['id']}/assignments/me", headers=organizer)
    assert mine.status_code == 200
    assert mine.json()["receiver_name"] == "Priya"
    theirs = client.get(f"/api/groups/{group['id']}/assignments/me", headers=priya)
    assert theirs.json()["receiver_name"] == "Rahul"


def test_assignment_privacy_secret_mode(client):
    group, organizer, priya, amit = _three_member_group(client)
    assert client.post(f"/api/groups/{group['id']}/assignments/draw", headers=organizer).status_code == 200
    hidden = client.get(f"/api/groups/{group['id']}/assignments", headers=priya)
    assert hidden.status_code == 403
    also_hidden = client.get(f"/api/groups/{group['id']}/assignments", headers=organizer)
    assert also_hidden.status_code == 403
    mine = client.get(f"/api/groups/{group['id']}/assignments/me", headers=priya)
    assert mine.status_code == 200
    assert "receiver_name" in mine.json()


def test_impossible_assignment_constraints_api(client):
    organizer = auth_header(client, "imp-org@example.com", "Rahul")
    group = _create_group(client, organizer, "Impossible")
    priya = auth_header(client, "imp-priya@example.com", "Priya")
    client.post(f"/api/invitations/{group['invite_code']}/join", headers=priya, json={"budget_acknowledged": True})
    members = client.get(f"/api/groups/{group['id']}/participants", headers=organizer).json()
    rahul = next(m for m in members if m["full_name"] == "Rahul")
    priya_p = next(m for m in members if m["full_name"] == "Priya")
    client.post(
        f"/api/groups/{group['id']}/exclusions",
        headers=organizer,
        json={"participant_id": rahul["id"], "excluded_participant_id": priya_p["id"], "reason": "couple"},
    )
    client.post(
        f"/api/groups/{group['id']}/exclusions",
        headers=organizer,
        json={"participant_id": priya_p["id"], "excluded_participant_id": rahul["id"], "reason": "couple"},
    )
    response = client.post(f"/api/groups/{group['id']}/assignments/draw", headers=organizer)
    assert response.status_code == 422
    assert "conflicts" in response.json()["detail"]
    leftover = client.get(f"/api/groups/{group['id']}/assignments/me", headers=organizer)
    assert leftover.status_code == 404


def test_concurrent_assignment_requests(client):
    group, organizer, priya, amit = _three_member_group(client)
    url = f"/api/groups/{group['id']}/assignments/draw"

    def _draw():
        return client.post(url, headers=organizer).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(pool.map(lambda _: _draw(), range(2)))
    assert 200 in codes
    assert codes.count(200) == 1
    assert all(code in {200, 409} for code in codes)


def test_gift_tracking(client):
    group, organizer, priya, amit = _three_member_group(client)
    client.post(f"/api/groups/{group['id']}/assignments/draw", headers=organizer)
    updated = client.patch(
        f"/api/groups/{group['id']}/gift-status",
        headers=priya,
        json={"gift_status": "purchased", "gift_description": "Wrapped mug"},
    )
    assert updated.status_code == 200
    progress = client.get(f"/api/groups/{group['id']}/gift-tracking", headers=organizer)
    assert progress.status_code == 200
    assert any(row["gift_status"] == "purchased" for row in progress.json())
    peek = client.get(f"/api/groups/{group['id']}/gift-tracking", headers=amit)
    assert peek.status_code == 200
    for row in peek.json():
        if row["full_name"] != "Amit":
            assert row["full_name"] in {"Participant", "You"}
