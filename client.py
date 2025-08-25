import socket
import tkinter as tk
from tkinter import messagebox, ttk
import json

HOST = "127.0.0.1"
PORT = 5000

class TicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Đặt Vé Xem Phim")

        # Giao diện nhập tên
        tk.Label(root, text="Tên của bạn:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(root, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        # Chọn phim
        tk.Label(root, text="Chọn phim:").grid(row=1, column=0, padx=5, pady=5)
        self.movie_var = tk.StringVar(value="Phim 1")
        movies = ["Phim 1", "Phim 2", "Phim 3"]
        self.movie_box = ttk.Combobox(root, textvariable=self.movie_var, values=movies, state="readonly")
        self.movie_box.grid(row=1, column=1, padx=5, pady=5)
        self.movie_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_seats())

        # Khung ghế
        self.seat_frame = tk.Frame(root)
        self.seat_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Tạo ghế (30 ghế: A1→F5)
        self.seat_buttons = {}
        rows = ["A", "B", "C", "D", "E", "F"]
        for i, row_name in enumerate(rows):
            for j in range(5):
                seat = f"{row_name}{j+1}"
                btn = tk.Button(self.seat_frame, text=seat, width=6, command=lambda s=seat: self.book_seat(s))
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.seat_buttons[seat] = btn
        # Danh sách vé đã đặt
        tk.Label(root, text="Vé đã đặt:").grid(row=3, column=0, columnspan=2)
        self.ticket_list = tk.Text(root, width=45, height=10, state="disabled")
        self.ticket_list.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Nút refresh
        tk.Button(root, text="Làm mới", command=self.refresh_seats).grid(row=5, column=0, columnspan=2, pady=5)

        self.refresh_seats()

    def send_request(self, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(message.encode("utf-8"))
                data = s.recv(4096).decode("utf-8")
            return data
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối server: {e}")
            return None

    def book_seat(self, seat):
        name = self.name_var.get().strip()
        movie = self.movie_var.get()
        if not name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên trước khi đặt vé.")
            return
        response = self.send_request(f"BOOK|{name}|{movie}|{seat}")
        if response and response.startswith("OK"):
            messagebox.showinfo("Thành công", f"Đặt ghế {seat} thành công!")
        else:
            messagebox.showerror("Thất bại", response.split("|")[1] if response else "Lỗi")
        self.refresh_seats()

    def refresh_seats(self):
        movie = self.movie_var.get()
        response = self.send_request(f"LIST|{movie}")
        if not response:
            return

        try:
            bookings = json.loads(response)
        except:
            bookings = []
        # Reset tất cả ghế
        for btn in self.seat_buttons.values():
            btn.config(state="normal", bg="SystemButtonFace")

        # Ghế đã đặt
        self.ticket_list.config(state="normal")
        self.ticket_list.delete(1.0, tk.END)

        for b in bookings:
            seat = b["seat"]
            name = b["name"]
            movie = b["movie"]

            if seat in self.seat_buttons:
                self.seat_buttons[seat].config(state="disabled", bg="red")

            # Hiển thị danh sách vé
            self.ticket_list.insert(tk.END, f"Tên: {name} | Phim: {movie} | Ghế: {seat}\n")

        self.ticket_list.config(state="disabled")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = TicketApp(root)
    root.mainloop()
