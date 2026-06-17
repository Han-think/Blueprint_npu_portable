"""
check_ollama.py — 돌려보기 전 연결 점검 + 다음 할 일 안내
========================================================
ollama / 모델 / Blueprint 서버 / schema 를 한 방에 점검한다. 의존 없음(urllib).

사용: python check_ollama.py
"""
from __future__ import annotations
import json
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OLLAMA = "http://127.0.0.1:11434"
BLUEPRINT = "http://127.0.0.1:8080"
WANT_MODEL = "qwen2.5"


def get(url, timeout=3):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return None, str(e)


def main():
    print("=== Blueprint 돌려보기 연결 점검 ===\n")
    todo = []

    # 1. ollama
    st, body = get(f"{OLLAMA}/api/tags")
    if st == 200:
        models = [m["name"] for m in json.loads(body).get("models", [])]
        print(f"[OK]   ollama 응답 ({OLLAMA}) — 모델 {len(models)}개: {models or '없음'}")
        if not any(WANT_MODEL in m for m in models):
            print(f"       ⚠ '{WANT_MODEL}' 계열 없음")
            todo.append(f"모델 받기:  ollama pull qwen2.5:7b")
    else:
        print(f"[ERR]  ollama 무응답 ({OLLAMA}) — 서버가 안 떠있음")
        todo.append("ollama 서버 기동:  C:\\Ollama-IPEX 에서 ollama serve  (또는 IPEX portable 시작 스크립트)")
        todo.append("그 다음 모델:  ollama pull qwen2.5:7b")

    # 2. Blueprint 서버
    st2, _ = get(f"{BLUEPRINT}/schema")
    if st2 == 200:
        print(f"[OK]   Blueprint 서버 응답 ({BLUEPRINT}/schema)")
    else:
        print(f"[--]   Blueprint 서버 미응답 ({BLUEPRINT}) — 아직 안 띄움")
        todo.append("Blueprint 서버 기동:  start.ps1  (UI + /schema /validate /output)")

    # 3. schema 파일
    sc = REPO / "00_contract" / "schema_v6.json"
    print(f"[{'OK' if sc.exists() else 'ERR'}]   계약 schema: {sc.relative_to(REPO) if sc.exists() else '없음'}")

    # 4. 학습 데이터(참고)
    tr = REPO / "20_dataset" / "train"
    n = sum(1 for f in tr.glob("blueprint_*_train.jsonl") for _ in open(f, encoding="utf-8")) if tr.exists() else 0
    dpo = (tr / "blueprint_preference_dpo.jsonl")
    nd = sum(1 for _ in open(dpo, encoding="utf-8")) if dpo.exists() else 0
    print(f"[OK]   학습셋 준비: SFT {n}행 + preference {nd}쌍")

    print("\n=== 다음 할 일 ===")
    if not todo:
        print("  모두 준비됨 → 브라우저에서 http://127.0.0.1:8080/Minimal.html 열고 brief 입력 → 생성")
    else:
        for i, t in enumerate(todo, 1):
            print(f"  {i}. {t}")
        print(f"  → 그 후: 브라우저 {BLUEPRINT}/Minimal.html 에서 모델 선택 → brief → 생성")
    print("\n자세한 단계: 30_model/RUN_GUIDE.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
