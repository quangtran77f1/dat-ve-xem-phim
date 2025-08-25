import socket
import threading
import json
import os

HOST = "127.0.0.1"
PORT = 5000

DATA_FILE = "data.json"

# Dữ liệu bookings lưu theo dạng:
# {
#   "Tên phim 1": [ { "name": ..., "seat": ..., "movie": ... }, ...],
#   "Tên phim 2": [ { ... } ],
# }
bookings = {}

# Load dữ liệu từ file
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        bookings = json.load(f)

lock = threading.Lock()

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=4, ensure_ascii=False)

def handle_client(conn, addr):
    print(f"[KẾT NỐI] Client {addr} đã kết nối.")
    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            parts = data.split("|")
            action = parts[0]

            if action == "BOOK":  # BOOK|Tên|Phim|Ghế
                name, movie, seat = parts[1], parts[2], parts[3]
                with lock:
                    if movie not in bookings:
                        bookings[movie] = []

                    # Kiểm tra ghế có ai đặt trong cùng phim chưa
                    if any(b["seat"] == seat for b in bookings[movie]):
                        conn.sendall("FAIL|Ghế đã có người đặt".encode("utf-8"))
                    else:
                        bookings[movie].append({"name": name, "movie": movie, "seat": seat})
                        save_data()
                        conn.sendall("OK|Đặt vé thành công".encode("utf-8"))

            elif action == "CANCEL":  # CANCEL|Tên|Phim|Ghế
                name, movie, seat = parts[1], parts[2], parts[3]
                with lock:
                    if movie in bookings:
                        bookings[movie] = [b for b in bookings[movie] if not (b["name"] == name and b["seat"] == seat)]
                        save_data()
                conn.sendall("OK|Hủy vé thành công".encode("utf-8"))

            elif action == "LIST":  # LIST|Phim
                movie = parts[1]
                with lock:
                    movie_bookings = bookings.get(movie, [])
                conn.sendall(json.dumps(movie_bookings, ensure_ascii=False).encode("utf-8"))

    except Exception as e:
        print(f"[LỖI] {e}")
    finally:
        conn.close()
        print(f"[NGẮT] Client {addr} đã ngắt kết nối.")


def start():
    print(f"[KHỞI ĐỘNG] Server chạy tại {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start()
