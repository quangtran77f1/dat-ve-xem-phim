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
if __name__ == "__main__":
    root = tk.Tk()
    app = TicketApp(root)
    root.mainloop()
