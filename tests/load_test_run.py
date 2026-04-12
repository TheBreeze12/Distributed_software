import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from jose import jwt

BASE_URL = "http://127.0.0.1"
PRODUCT_NAME = "pressure_phone"
SECRET_KEY = "3x@mpl3$eCreT!Key2026$gHjklQwErTyUiOpZxcVbnM9"
ALGORITHM = "HS256"


def post_json(path: str, payload: dict, token: str | None = None):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body}


def get_json(path: str, token: str | None = None):
    req = urllib.request.Request(BASE_URL + path, method="GET")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        if not body:
            return resp.status, {}
        try:
            return resp.status, json.loads(body)
        except Exception:
            return resp.status, {"raw": body}


def token_for_user_id(u_id: int) -> str:
    return jwt.encode({"sub": str(u_id)}, SECRET_KEY, algorithm=ALGORITHM)


def create_order(token: str):
    return post_json(
        "/api/v1/orders/create",
        {"p_name": PRODUCT_NAME, "quantity": 1},
        token=token,
    )


def scenario_same_user_repeat():
    token = token_for_user_id(1001)
    results = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = [ex.submit(create_order, token) for _ in range(20)]
        for fut in as_completed(futs):
            results.append(fut.result())

    accepted = sum(1 for code, body in results if code == 200)
    rejected = len(results) - accepted
    print("SCENARIO_A same-user repeat")
    print(json.dumps({"accepted": accepted, "rejected": rejected}, ensure_ascii=False))
    return results


def scenario_multi_user_one_product():
    tokens = [token_for_user_id(2000 + i) for i in range(30)]

    results = []
    with ThreadPoolExecutor(max_workers=30) as ex:
        futs = [ex.submit(create_order, token) for token in tokens]
        for fut in as_completed(futs):
            results.append(fut.result())

    accepted = sum(1 for code, body in results if code == 200)
    rejected = len(results) - accepted
    print("SCENARIO_B multi-user one-product")
    print(json.dumps({"accepted": accepted, "rejected": rejected}, ensure_ascii=False))
    return results


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"

    code, _ = get_json("/api/v1/products")
    if code != 200:
        raise RuntimeError("service not ready")

    if phase in ("a", "all"):
        scenario_same_user_repeat()
        time.sleep(6)

    if phase in ("b", "all"):
        scenario_multi_user_one_product()
        time.sleep(8)


if __name__ == "__main__":
    main()
