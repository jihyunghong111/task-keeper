from sqlalchemy import event


def test_create_and_list(client):
    res = client.post("/tasks", json={"title": "테스트 할 일", "tags": ["개인", "긴급"]})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "테스트 할 일"
    assert {t["name"] for t in body["tags"]} == {"개인", "긴급"}

    res = client.get("/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["tags"]


def test_list_tasks_no_n_plus_one(client, db_session):
    for i in range(5):
        client.post("/tasks", json={"title": f"할 일 {i}", "tags": ["공통"]})

    queries = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(db_session.bind, "before_cursor_execute", before_cursor_execute)
    try:
        res = client.get("/tasks")
    finally:
        event.remove(db_session.bind, "before_cursor_execute", before_cursor_execute)

    assert res.status_code == 200
    assert len(res.json()) == 5
    # 할 일 목록 SELECT 1회 + 태그 selectin SELECT 1회 = 할 일 개수와 무관하게 고정
    assert len(queries) <= 2
