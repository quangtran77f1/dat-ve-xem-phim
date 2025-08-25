import socket
import json
import tkinter as tk
from tkinter import messagebox, ttk  # thêm ttk để dùng Combobox

HOST = "127.0.0.1"
PORT = 65432

def send_request(request):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(request).encode())
            data = s.recv(4096).decode()
            return json.loads(data)
    except Exception as e:
        return {"status": "error", "message": str(e)}

class TicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống đặt vé xem phim")

        tk.Label(root, text="Tên người dùng:").grid(row=0, column=0)
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=0, column=1)

        # Combobox chọn phim
        tk.Label(root, text="Chọn phim:").grid(row=1, column=0)
        self.movie_var = tk.StringVar()
        self.movie_combo = ttk.Combobox(root, textvariable=self.movie_var, state="readonly")
        self.movie_combo['values'] = ("Avengers", "Batman", "Spiderman")
        self.movie_combo.grid(row=1, column=1)
        self.movie_combo.current(0)  # mặc định chọn Avengers

        self.seat_frame = tk.Frame(root)
        self.seat_frame.grid(row=2, column=0, columnspan=2)

        tk.Button(root, text="Tải ghế", command=self.load_seats).grid(row=3, column=0)
        tk.Button(root, text="Vé của tôi", command=self.show_my_tickets).grid(row=3, column=1)

        self.ticket_listbox = tk.Listbox(root, width=40, height=10)
        self.ticket_listbox.grid(row=4, column=0, columnspan=2)

        tk.Button(root, text="Hủy vé đã chọn", command=self.cancel_ticket).grid(row=5, column=0, columnspan=2)

    def load_seats(self):
        for widget in self.seat_frame.winfo_children():
            widget.destroy()

        movie = self.movie_var.get()
        response = send_request({"action": "list", "movie": movie})
        if response["status"] == "ok":
            seats = response["seats"]
            booked = response["booked"]

            for idx, seat in enumerate(seats):
                btn = tk.Button(self.seat_frame, text=seat,
                                state=("disabled" if seat in booked else "normal"),
                                command=lambda s=seat: self.book_seat(movie, s))
                btn.grid(row=idx // 10, column=idx % 10, padx=2, pady=2)
        else:
            messagebox.showerror("Lỗi", response["message"])

    def book_seat(self, movie, seat):
        user = self.username_entry.get()
        if not user:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên người dùng")
            return

        response = send_request({"action": "book", "movie": movie, "seat": seat, "user": user})
        messagebox.showinfo("Thông báo", response.get("message", ""))
        self.load_seats()

    def show_my_tickets(self):
        self.ticket_listbox.delete(0, tk.END)
        user = self.username_entry.get()
        response = send_request({"action": "mytickets", "user": user})
        if response["status"] == "ok":
            for t in response["tickets"]:
                self.ticket_listbox.insert(tk.END, f"{t['movie']} - Ghế {t['seat']}")
        else:
            messagebox.showerror("Lỗi", response["message"])

    def cancel_ticket(self):
        user = self.username_entry.get()
        selection = self.ticket_listbox.curselection()
        if not selection:
            messagebox.showwarning("Lỗi", "Vui lòng chọn vé để hủy")
            return

        ticket_text = self.ticket_listbox.get(selection[0])
        movie, seat = ticket_text.split(" - Ghế ")
        response = send_request({"action": "cancel", "user": user, "movie": movie, "seat": seat})
        messagebox.showinfo("Thông báo", response.get("message", ""))
        self.show_my_tickets()
        self.load_seats()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketApp(root)
    root.mainloop()
