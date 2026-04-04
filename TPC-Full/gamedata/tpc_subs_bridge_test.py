import os
import time
import threading
import socket

from twitch_bridge_config import TWITCH_NICK, TWITCH_TOKEN, TWITCH_CHANNEL

try:
    import msvcrt  # Windows only
except ImportError:
    msvcrt = None

QUEUE_FILENAME = "tpc_subs_queue.txt"


def get_game_root() -> str:
    current = os.path.abspath(os.path.dirname(__file__))

    for _ in range(10):
        if os.path.exists(os.path.join(current, "bin")):
            return current
        if os.path.exists(os.path.join(current, "gamedata")):
            return current

        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return os.getcwd()


GAME_ROOT = get_game_root()
OUTPUT_FILE = os.path.join(GAME_ROOT, "gamedata", "scripts", QUEUE_FILENAME)


def log(msg: str) -> None:
    print(f"[TPC-SUBS-TEST] {msg}")


def sanitize_field(text: str) -> str:
    return (
        str(text if text is not None else "")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "/")
        .strip()
    )


def ensure_queue_exists() -> None:
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("")


def clear_queue() -> None:
    ensure_queue_exists()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")
    log(f"Cleared queue: {OUTPUT_FILE}")


def append_sub_event(user: str, event_type: str, tier: str, message: str = "") -> None:
    ensure_queue_exists()

    line = (
        f"{sanitize_field(user)}|"
        f"{sanitize_field(event_type)}|"
        f"{sanitize_field(tier)}|"
        f"{sanitize_field(message)}"
    )

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    log(f"Wrote event: {line}")


def key_listener() -> None:
    if not msvcrt:
        log("Key listener not supported on this OS")
        return

    log("Test keys active:")
    log("  1 = tier1 sub")
    log("  2 = tier2 sub")
    log("  3 = tier3 sub")
    log("  4 = tier1 resub")
    log("  5 = gifted sub")
    log("  c = clear queue")
    log("  q = quit")

    while True:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8", errors="ignore").lower()

                if key == "1":
                    append_sub_event("TestSub_T1", "sub", "tier1", "")
                elif key == "2":
                    append_sub_event("TestSub_T2", "sub", "tier2", "")
                elif key == "3":
                    append_sub_event("TestSub_T3", "sub", "tier3", "")
                elif key == "4":
                    append_sub_event("Returner", "resub", "tier1", "Glad to be back")
                elif key == "5":
                    append_sub_event("GiftGoblin", "sub_gift", "tier1", "")
                elif key == "c":
                    clear_queue()
                elif key == "q":
                    log("Quitting test injector")
                    os._exit(0)

                time.sleep(0.1)

        except Exception as e:
            log(f"Key listener error: {e}")
            time.sleep(0.25)


def main() -> None:
    log(f"Game root: {GAME_ROOT}")
    log(f"Queue file: {OUTPUT_FILE}")

    clear_queue()

    t = threading.Thread(target=key_listener, daemon=True)
    t.start()

    log("Ready. Press keys to inject sub events.")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()