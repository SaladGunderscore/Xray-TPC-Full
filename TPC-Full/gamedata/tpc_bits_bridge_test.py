import os
import re
import socket
import time
import traceback
import threading

try:
    import msvcrt  # Windows only
except ImportError:
    msvcrt = None

from twitch_bridge_config import TWITCH_NICK, TWITCH_TOKEN, TWITCH_CHANNEL

# =========================
# CONFIG
# =========================

QUEUE_FILENAME = "tpc_bits_queue.txt"
RECONNECT_DELAY = 5
SOCKET_TIMEOUT = 1.0


# =========================
# PATHS
# =========================

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
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)


# =========================
# HELPERS
# =========================

def log(msg: str) -> None:
    print(f"[TPC-BITS] {msg}")


def sanitize_field(text: str) -> str:
    return (
        str(text if text is not None else "")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "/")
        .strip()
    )


def clear_queue_file() -> None:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")
    log(f"Queue cleared: {OUTPUT_FILE}")


def append_bits_event(user: str, bits: int, event_type: str, message: str) -> None:
    user = sanitize_field(user)
    bits = int(bits)
    event_type = sanitize_field(event_type)
    message = sanitize_field(message)

    line = f"{user}|{bits}|{event_type}|{message}"

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    log(f"Wrote event: {line}")


def parse_irc_tags(raw_line: str) -> dict:
    tags = {}

    if not raw_line.startswith("@"):
        return tags

    try:
        tag_blob = raw_line.split(" ", 1)[0][1:]
        for pair in tag_blob.split(";"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                tags[key] = value
            else:
                tags[pair] = ""
    except Exception:
        pass

    return tags


def parse_privmsg(raw_line: str) -> tuple[str | None, str | None]:
    if "PRIVMSG" not in raw_line:
        return None, None

    try:
        line = raw_line
        if line.startswith("@"):
            first_space = line.find(" ")
            if first_space != -1:
                line = line[first_space + 1:]

        prefix, trailing = line.split(" :", 1)
        user = prefix.split("!", 1)[0].lstrip(":")
        message = trailing.strip()

        return user, message
    except Exception:
        return None, None


def extract_bits_from_message(message: str) -> int:
    if not message:
        return 0

    total = 0
    for match in re.finditer(r"(?i)\bcheer(\d+)\b", message):
        try:
            total += int(match.group(1))
        except ValueError:
            continue

    return total


# =========================
# TWITCH IRC
# =========================

def connect() -> socket.socket:
    log("Connecting to Twitch IRC...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("irc.chat.twitch.tv", 6667))

    sock.send("CAP REQ :twitch.tv/tags twitch.tv/commands\r\n".encode("utf-8"))
    sock.send(f"PASS {TWITCH_TOKEN}\r\n".encode("utf-8"))
    sock.send(f"NICK {TWITCH_NICK}\r\n".encode("utf-8"))
    sock.send(f"JOIN {TWITCH_CHANNEL}\r\n".encode("utf-8"))

    sock.settimeout(5.0)

    try:
        for _ in range(12):
            data = sock.recv(4096).decode("utf-8", errors="ignore").strip()
            if not data:
                continue

            for line in data.split("\r\n"):
                line = line.strip()
                if not line:
                    continue

                log(f"IRC: {line}")

                if "Login authentication failed" in line:
                    raise RuntimeError("Login authentication failed")
                if "Improperly formatted auth" in line:
                    raise RuntimeError("Improperly formatted auth token")
    except socket.timeout:
        pass

    sock.settimeout(SOCKET_TIMEOUT)
    log("Connected and ready")
    return sock


def handle_line(raw_line: str) -> None:
    if not raw_line:
        return

    tags = parse_irc_tags(raw_line)

    if "PRIVMSG" not in raw_line:
        return

    user, message = parse_privmsg(raw_line)
    if not user:
        return

    bits_value = 0
    bits_tag = tags.get("bits", "")
    if bits_tag:
        try:
            bits_value = int(bits_tag)
        except ValueError:
            bits_value = 0

    if bits_value <= 0:
        bits_value = extract_bits_from_message(message or "")

    if bits_value <= 0:
        return

    log(f"Cheer detected from {user}: {bits_value} bits | {message}")
    append_bits_event(user, bits_value, "cheer", message or "")


# =========================
# KEY TESTER
# =========================

def test_key_listener() -> None:
    if not msvcrt:
        log("Key listener not supported on this OS")
        return

    log("Test keys active:")
    log("  1 = 25 bits")
    log("  2 = 100 bits")
    log("  3 = 500 bits")
    log("  4 = 1000 bits")
    log("  5 = 5000 bits")
    log("  0 = 10000 bits")

    while True:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8", errors="ignore")

                if key == "1":
                    append_bits_event("MonolithBank", 25, "test", "keypress 25")
                elif key == "2":
                    append_bits_event("MonolithBank", 100, "test", "keypress 100")
                elif key == "3":
                    append_bits_event("MonolithBank", 500, "test", "keypress 500")
                elif key == "4":
                    append_bits_event("MonolithBank", 1000, "test", "keypress 1000")
                elif key == "5":
                    append_bits_event("MonolithBank", 5000, "test", "keypress 5000")
                elif key == "0":
                    append_bits_event("MonolithBank", 10000, "test", "keypress 10000")

                time.sleep(0.1)

        except Exception as e:
            log(f"Key listener error: {e}")
            time.sleep(0.25)


# =========================
# MAIN LOOP
# =========================

def main() -> None:
    log(f"Game root: {GAME_ROOT}")
    log(f"Queue file: {OUTPUT_FILE}")

    clear_queue_file()

    threading.Thread(target=test_key_listener, daemon=True).start()

    while True:
        try:
            sock = connect()
            buffer = ""

            while True:
                try:
                    chunk = sock.recv(4096).decode("utf-8", errors="ignore")
                    if not chunk:
                        raise ConnectionError("No data received")

                    buffer += chunk

                    while "\r\n" in buffer:
                        raw_line, buffer = buffer.split("\r\n", 1)
                        raw_line = raw_line.strip()

                        if not raw_line:
                            continue

                        if raw_line.startswith("PING"):
                            sock.send(raw_line.replace("PING", "PONG", 1).encode("utf-8") + b"\r\n")
                            continue

                        handle_line(raw_line)

                except socket.timeout:
                    continue
                except Exception as inner_e:
                    log(f"Inner error: {inner_e}")
                    break

        except KeyboardInterrupt:
            log("Stopped by user")
            return
        except Exception as e:
            log(f"Connection failed: {e}")
            log(traceback.format_exc())
            log(f"Reconnecting in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    main()