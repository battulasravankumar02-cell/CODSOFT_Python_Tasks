import urllib.request
import json
import http.cookiejar

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

# 1. GET /
req = urllib.request.Request("http://127.0.0.1:5000/")
with opener.open(req) as resp:
    html = resp.read().decode('utf-8')
    assert resp.status == 200
    assert "SINGLE PLAYER" in html
    assert "DUO PLAYER" in html
    assert "SCORE" in html
    assert "THEME" in html
    assert "Make your move!" in html
    print("[PASS] GET / returned 200 OK with all 4 working tabs in UI.")

# 2. Single Player: POST /play with 'rock'
req = urllib.request.Request(
    "http://127.0.0.1:5000/play",
    data=json.dumps({"choice": "rock"}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data["success"] is True
    assert data["round"]["user_choice"] == "rock"
    print(f"[PASS] Single Player Round 1: Rock vs {data['round']['computer_label']} -> {data['round']['result_title']}")

# 3. Duo Player Setup: Rahul vs Arjun
req = urllib.request.Request(
    "http://127.0.0.1:5000/duo-setup",
    data=json.dumps({"p1_name": "Rahul", "p2_name": "Arjun"}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data["success"] is True
    assert data["p1_name"] == "Rahul"
    assert data["p2_name"] == "Arjun"
    print(f"[PASS] Duo Player Setup: {data['p1_name']} vs {data['p2_name']} initialized.")

# 4. Duo Player Round: Rahul chooses Rock, Arjun chooses Scissors
req = urllib.request.Request(
    "http://127.0.0.1:5000/play-duo",
    data=json.dumps({
        "p1_name": "Rahul",
        "p2_name": "Arjun",
        "p1_choice": "rock",
        "p2_choice": "scissors"
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data["success"] is True
    assert data["round"]["result"] == "p1_win"
    assert data["scores"]["p1"] == 1
    assert data["scores"]["p2"] == 0
    print(f"[PASS] Duo Round 1: Rahul (Rock) vs Arjun (Scissors) -> {data['round']['result_title']} | Scores: P1={data['scores']['p1']}, P2={data['scores']['p2']}")

# 5. GET /get-scores to verify Score Tab data
req = urllib.request.Request("http://127.0.0.1:5000/get-scores")
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data["success"] is True
    assert data["single"]["user"] >= 0
    assert data["duo"]["p1_name"] == "Rahul"
    assert data["duo"]["p1_score"] == 1
    print(f"[PASS] GET /get-scores accurately returned active session scores: {data}")

# 6. POST /reset (Simulates clicking RESET SCORE in Score Tab)
req = urllib.request.Request(
    "http://127.0.0.1:5000/reset",
    data=b"{}",
    headers={"Content-Type": "application/json"}
)
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data["success"] is True
    assert data["single"]["user"] == 0
    assert data["single"]["computer"] == 0
    assert data["duo"]["p1_score"] == 0
    assert data["duo"]["p2_score"] == 0
    assert data["duo"]["active"] is False
    print(f"[PASS] POST /reset successfully cleared all single and duo player scores to 0.")

# 7. Workflow: New Duo match with different players (Sravan and Kiran) after reset
req = urllib.request.Request(
    "http://127.0.0.1:5000/duo-setup",
    data=json.dumps({"p1_name": "Sravan", "p2_name": "Kiran"}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data["success"] is True
    assert data["p1_name"] == "Sravan"
    assert data["p2_name"] == "Kiran"
    print(f"[PASS] New match workflow tested: {data['p1_name']} vs {data['p2_name']} created cleanly after score reset.")

print("\nALL LIVE INTEGRATION AND EXTENDED WORKFLOW TESTS PASSED!")
