import socket
import time
import os
import traceback
import twitch_bridge_config

from twitch_bridge_config import TWITCH_NICK, TWITCH_TOKEN, TWITCH_CHANNEL


def get_game_root():
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
OUTPUT_FILE = os.path.join(GAME_ROOT, "gamedata", "scripts", "twitch_chat_queue.txt")

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

print(f"[TwitchBridge] Game root: {GAME_ROOT}")
print(f"[TwitchBridge] Queue file: {OUTPUT_FILE}")

def connect():
    print("[TwitchBridge] Connecting to Twitch IRC...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("irc.chat.twitch.tv", 6667))

    sock.send(f"PASS {TWITCH_TOKEN}\r\n".encode("utf-8"))
    sock.send(f"NICK {TWITCH_NICK}\r\n".encode("utf-8"))
    sock.send(f"JOIN {TWITCH_CHANNEL}\r\n".encode("utf-8"))

    sock.settimeout(5.0)

    try:
        for _ in range(10):
            data = sock.recv(2048).decode("utf-8", errors="ignore").strip()
            if not data:
                continue

            for line in data.split("\r\n"):
                line = line.strip()
                if not line:
                    continue

                print(f"[Twitch Response] {line}")

                if "Login authentication failed" in line:
                    raise RuntimeError("Login authentication failed")
                if "Improperly formatted auth" in line:
                    raise RuntimeError("Improperly formatted auth token")

    except socket.timeout:
        pass

    sock.settimeout(1.0)
    print("[TwitchBridge] Connected and ready")
    return sock

def parse_message(raw):
    if "PRIVMSG" not in raw:
        return None, None

    try:
        user = raw.split("!")[0].lstrip(":")
        msg = raw.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
        return user, msg
    except Exception:
        return None, None

def sanitize_field(text):
    if text is None:
        return ""

    return (
        str(text)
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "/")
        .strip()
    )

def append_message(user, msg):
    try:
        user = sanitize_field(user)
        msg = sanitize_field(msg)

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user}|{msg}\n")

    except Exception as e:
        print(f"[TwitchBridge] ERROR appending message: {e}")

def clear_queue_file():
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("")
    except Exception as e:
        print(f"[TwitchBridge] ERROR clearing queue file: {e}")

def main():
    clear_queue_file()
    print("[TwitchBridge] Queue cleared on startup")

    while True:
        try:
            sock = connect()

            while True:
                try:
                    data = sock.recv(2048).decode("utf-8", errors="ignore")

                    if not data:
                        raise ConnectionError("No data received")

                    for line in data.split("\r\n"):
                        line = line.strip()
                        if not line:
                            continue

                        if line.startswith("PING"):
                            pong = line.replace("PING", "PONG", 1) + "\r\n"
                            sock.send(pong.encode("utf-8"))
                            continue

                        user, msg = parse_message(line)
                        if user and msg:
                            print(f"[{user}] {msg}")
                            append_message(user, msg)

                except socket.timeout:
                    continue
                except Exception as inner_e:
                    print(f"[TwitchBridge] Inner error: {inner_e}")
                    break

        except Exception as e:
            print(f"[TwitchBridge] Connection failed: {e}")
            print(traceback.format_exc())
            print("[TwitchBridge] Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    print("[TwitchBridge] Starting Twitch -> STALKER bridge...")
    main()