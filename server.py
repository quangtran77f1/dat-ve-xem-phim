import socket
import threading
import json

# Danh sách phim có 30 ghế mỗi phim
movies = {
    "Avengers": [f"{row}{num}" for row in ["A","B","C"] for num in range(1, 11)],
    "Batman":   [f"{row}{num}" for row in ["A","B","C"] for num in range(1, 10+1)],
    "Spiderman":[f"{row}{num}" for row in ["A","B","C"] for num in range(1, 10+1)]
}

# bookings = { "TênPhim": [ { "user": "Tên", "seat": "A1" }, ... ] }
bookings = {movie: [] for movie in movies}

lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[Kết nối] {addr} đã kết nối")
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            request = json.loads(data)
            action = request.get("action")

            response = {"status": "error", "message": "Yêu cầu không hợp lệ"}

            with lock:
                if action == "list":
                    movie = request.get("movie")
                    if movie in movies:
                        booked = [b["seat"] for b in bookings[movie]]
                        response = {"status": "ok", "seats": movies[movie], "booked": booked}
                    else:
                        response = {"status": "error", "message": "Phim không tồn tại"}

                elif action == "book":
                    movie = request.get("movie")
                    seat = request.get("seat")
                    user = request.get("user")
                    if movie in movies and seat in movies[movie]:
                        if seat not in [b["seat"] for b in bookings[movie]]:
                            bookings[movie].append({"user": user, "seat": seat})
                            response = {"status": "ok", "message": f"Đặt ghế {seat} thành công cho {user}"}
                        else:
                            response = {"status": "error", "message": "Ghế đã có người đặt"}
                    else:
                        response = {"status": "error", "message": "Phim hoặc ghế không hợp lệ"}

                elif action == "mytickets":
                    user = request.get("user")
                    user_tickets = []
                    for m, blist in bookings.items():
                        for b in blist:
                            if b["user"] == user:
                                user_tickets.append({"movie": m, "seat": b["seat"]})
                    response = {"status": "ok", "tickets": user_tickets}

                elif action == "cancel":
                    user = request.get("user")
                    movie = request.get("movie")
                    seat = request.get("seat")
                    if movie in bookings:
                        before = len(bookings[movie])
                        bookings[movie] = [b for b in bookings[movie] if not (b["user"] == user and b["seat"] == seat)]
                        after = len(bookings[movie])
                        if before != after:
                            response = {"status": "ok", "message": f"Đã hủy vé {seat} - {movie}"}
                        else:
                            response = {"status": "error", "message": "Không tìm thấy vé để hủy"}
                    else:
                        response = {"status": "error", "message": "Phim không tồn tại"}

            conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print("Lỗi:", e)
    finally:
        conn.close()
        print(f"[Ngắt kết nối] {addr}")

def start_server():
    host = "127.0.0.1"
    port = 65432
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[Server] Đang lắng nghe tại {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
