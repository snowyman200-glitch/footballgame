import os
import json
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")

app = FastAPI(title="World Cup Pick'em API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing")
    return psycopg.connect(DATABASE_URL)


class UserPayload(BaseModel):
    telegram_user_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None


class SubmissionPayload(BaseModel):
    tournament_slug: str
    user: UserPayload
    bracket_payload: dict[str, Any]


class SnapshotPayload(BaseModel):
    payload: dict[str, Any]


@app.get('/health')
def health():
    return {'ok': True}


@app.get('/api/tournament/{slug}')
def tournament(slug: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id, slug, title, status from tournaments where slug = %s limit 1", (slug,))
            t = cur.fetchone()
            if not t:
                raise HTTPException(status_code=404, detail='Tournament not found')
            cur.execute(
                """
                select match_number, stage, group_code, home_team, away_team, kickoff_at, is_locked
                from matches m
                join tournaments t on t.id = m.tournament_id
                where t.slug = %s
                order by match_number asc
                """,
                (slug,),
            )
            matches = cur.fetchall()
    return {
        'tournament': {'id': str(t[0]), 'slug': t[1], 'title': t[2], 'status': t[3]},
        'matches': [
            {
                'match_number': m[0], 'stage': m[1], 'group_code': m[2],
                'home_team': m[3], 'away_team': m[4],
                'kickoff_at': m[5].isoformat() if m[5] else None,
                'is_locked': m[6]
            } for m in matches
        ]
    }


@app.post('/api/submissions')
def save_submission(payload: SubmissionPayload):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id from tournaments where slug = %s limit 1", (payload.tournament_slug,))
            t = cur.fetchone()
            if not t:
                raise HTTPException(status_code=404, detail='Tournament not found')
            tournament_id = t[0]
            cur.execute(
                """
                insert into users (telegram_user_id, username, first_name, last_name, language_code)
                values (%s, %s, %s, %s, %s)
                on conflict (telegram_user_id)
                do update set
                  username = excluded.username,
                  first_name = excluded.first_name,
                  last_name = excluded.last_name,
                  language_code = excluded.language_code,
                  updated_at = now()
                returning id
                """,
                (
                    payload.user.telegram_user_id,
                    payload.user.username,
                    payload.user.first_name,
                    payload.user.last_name,
                    payload.user.language_code,
                ),
            )
            user_id = cur.fetchone()[0]
            cur.execute(
                """
                insert into tournament_submissions (tournament_id, user_id, bracket_payload)
                values (%s, %s, %s)
                on conflict (tournament_id, user_id)
                do update set bracket_payload = excluded.bracket_payload, submitted_at = now()
                returning id, submitted_at
                """,
                (tournament_id, user_id, json.dumps(payload.bracket_payload)),
            )
            row = cur.fetchone()
        conn.commit()
    return {'submission_id': str(row[0]), 'submitted_at': row[1].isoformat()}


@app.get('/api/community/{slug}')
def get_community(slug: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select cs.payload, cs.created_at
                from community_snapshots cs
                join tournaments t on t.id = cs.tournament_id
                where t.slug = %s
                order by cs.created_at desc
                limit 1
                """,
                (slug,),
            )
            row = cur.fetchone()
    if not row:
        return {
            'items': [
                {'label': 'Чемпион', 'leader': 'Бразилия', 'share': '31%'},
                {'label': 'Финалист', 'leader': 'Франция', 'share': '18%'},
                {'label': 'Популярный апсет', 'leader': 'ЮАР выходит из группы A', 'share': '14%'}
            ]
        }
    return {'snapshot': row[0], 'created_at': row[1].isoformat()}


@app.post('/api/admin/community/{slug}')
def save_community(slug: str, body: SnapshotPayload):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id from tournaments where slug = %s limit 1", (slug,))
            t = cur.fetchone()
            if not t:
                raise HTTPException(status_code=404, detail='Tournament not found')
            cur.execute(
                "insert into community_snapshots (tournament_id, snapshot_type, payload) values (%s, %s, %s) returning id",
                (t[0], 'manual', json.dumps(body.payload)),
            )
            row = cur.fetchone()
        conn.commit()
    return {'snapshot_id': str(row[0])}
