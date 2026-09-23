"""Terminal chat client for testing Sakhi without the frontend."""

import httpx

API = "http://localhost:8000/api/chat"
session_id = ""
messages = []


def send(text: str) -> dict:
    global session_id
    messages.append(f"Patient: {text}")
    conversation = "\n".join(messages)

    resp = httpx.post(API, json={"conversation": conversation, "session_id": session_id}, timeout=60)
    if resp.status_code != 200:
        print(f"\033[91mError {resp.status_code}: {resp.text}\033[0m")
        return None
    data = resp.json()

    session_id = data["session_id"]
    messages.append(f"Sakhi: {data['reply']}")
    return data


def main():
    print("=" * 50)
    print("  Sakhi Health Navigator - Terminal Test")
    print("  Type 'quit' to exit")
    print("=" * 50)
    print()

    while True:
        text = input("\033[95mYou: \033[0m").strip()
        if not text:
            continue
        if text.lower() in ("quit", "exit", "q"):
            break

        data = send(text)
        if data is None:
            continue

        # show reply
        print(f"\033[96mSakhi: \033[0m{data['reply']}")

        # show crisis banner
        if data.get("crisis"):
            print("\033[91m⚠ CRISIS: 112 | iCall: 9152987821 | Women Helpline: 1800-599-0019\033[0m")

        # show providers if any
        providers = data.get("ranked_providers", [])
        if providers:
            print(f"\n\033[93m--- {len(providers)} providers found ---\033[0m")
            for i, p in enumerate(providers[:10], 1):
                score = p.get("total_score", 0)
                name = p.get("name", "Unknown")
                pid = p.get("provider_id", "")
                city = p.get("city", "")
                unverified = p.get("unverified_factors", [])
                source = " [web]" if pid.startswith("web_") else ""
                tag = " [unverified]" if unverified else ""
                print(f"  {i}. {name} - {city} (score: {score}){source}{tag}")
            if len(providers) > 10:
                print(f"  ... and {len(providers) - 10} more")
            print()

        print()


if __name__ == "__main__":
    main()
