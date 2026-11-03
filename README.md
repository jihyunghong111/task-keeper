# task-keeper

개인 할 일을 관리하는 작은 웹 API입니다. 책 3장의 스킬 실습용 예제 저장소입니다.

- 스택: Python, FastAPI, SQLAlchemy, SQLite
- 패키지 관리: uv
- 기본 브랜치: main

## 구조

```
task-keeper/
├── app/
│   ├── main.py              # FastAPI 앱과 엔드포인트
│   ├── database.py          # 엔진, 세션, Base
│   ├── models.py            # Task, Tag (다대다)
│   ├── schemas.py           # 응답/요청 스키마
│   └── services/
│       └── task_service.py  # list_tasks() 에 N+1 버그
├── scripts/
│   └── seed.py              # 데모 데이터 생성
├── tests/
│   ├── conftest.py          # 메모리 DB, 테스트 클라이언트
│   └── test_smoke.py        # 기본 동작 확인
├── pyproject.toml          # 의존성과 프로젝트 메타데이터
└── uv.lock                 # 잠금 파일
```

## 실행

uv가 설치돼 있어야 합니다. 없으면 https://docs.astral.sh/uv/ 를 보고 설치하세요.

```
uv sync                              # 의존성 설치 + 가상환경 생성
uv run python scripts/seed.py        # 데모 할 일 100개 생성
uv run uvicorn app.main:app --reload
```

- API 문서: http://127.0.0.1:8000/docs
- 목록 조회: http://127.0.0.1:8000/tasks

## 엔드포인트

- `GET /tasks` 할 일 목록
- `POST /tasks` 할 일 생성. 본문 예: `{"title": "장보기", "tags": ["개인", "쇼핑"]}`
- `GET /tasks/{id}` 단건 조회

## 해결된 이슈: 목록 조회 N+1 (#1, #2)

`list_tasks()`가 할 일을 조회한 뒤 각 할 일의 태그를 따로 조회해 할 일 개수만큼 쿼리가 추가로 실행되는 N+1 문제가 있었으나, `selectinload`를 적용해 해결했습니다.

```python
from sqlalchemy.orm import selectinload

tasks = db.query(Task).options(selectinload(Task.tags)).all()
```

실제 쿼리 수를 확인하려면 echo를 켜고 실행하세요.

```
SQLALCHEMY_ECHO=1 uv run uvicorn app.main:app
```

이 변경이 책 3.8 실습의 작업 내용입니다. 이슈 생성부터 커밋, PR, 리뷰, 리뷰 반영까지 다섯 스킬로 처리합니다.

## 테스트

```
uv run pytest
```
