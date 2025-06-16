import threading
import random
from socket import *
from customtkinter import *

set_appearance_mode("system")
set_default_color_theme("blue")


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x450")
        self.minsize(400, 300)
        self.title("Чат")

        self.username = None

        # ======== Верхня панель (Ім’я + тема) ========
        self.top_frame = CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.name_label = CTkLabel(self.top_frame, text="Ваше ім’я:")
        self.name_label.pack(side="left")

        self.name_entry = CTkEntry(self.top_frame, placeholder_text="Ім'я")
        self.name_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.rename_button = CTkButton(self.top_frame, text="Змінити ім’я", width=100, command=self.rename)
        self.rename_button.pack(side="left", padx=5)

        self.theme_menu = CTkOptionMenu(self.top_frame, values=["Темна", "Світла"], command=self.change_theme)
        self.theme_menu.pack(side="right")

        # ======== Область чату ========
        self.chat_frame = CTkFrame(self)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.chat_text = CTkTextbox(self.chat_frame, wrap="word", activate_scrollbars=False)
        self.chat_text.insert("0.0", "Тут буде історія повідомлень...\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = CTkScrollbar(self.chat_frame, command=self.chat_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.chat_text.configure(yscrollcommand=self.scrollbar.set)

        # ======== Ввід повідомлення ========
        self.bottom_frame = CTkFrame(self)
        self.bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.message_input = CTkEntry(self.bottom_frame, placeholder_text="Введіть повідомлення:")
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.send_button = CTkButton(self.bottom_frame, text="▶", width=40, command=self.send_message)
        self.send_button.pack(side="right")

        # ======== Підключення до сервера ========
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))

            # Генерація початкового імені
            name = self.name_entry.get().strip()
            if name:
                self.username = name
            else:
                self.username = f"Ви_{random.randint(1000, 9999)}"
                self.name_entry.insert(0, self.username)

            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.sendall(hello.encode("utf-8"))

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.add_message(f"[Помилка] Не вдалося підключитися до сервера: {e}")

    def change_theme(self, value):
        if value == "Темна":
            set_appearance_mode("dark")
        elif value == "Світла":
            set_appearance_mode("light")
        else:
            set_appearance_mode("system")

    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            full_message = f"{self.username}: {message}"
            self.add_message(full_message)
            try:
                self.sock.sendall(f"TEXT@{self.username}@{message}\n".encode("utf-8"))
            except:
                self.add_message("[Помилка] Повідомлення не надіслано.")
            self.message_input.delete(0, "end")

    def add_message(self, message):
        self.chat_text.configure(state="normal")
        self.chat_text.insert("end", message + "\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_server_message(line.strip())
            except:
                break
        self.sock.close()

    def handle_server_message(self, line):
        if not line:
            return
        parts = line.split("@", 2)
        if len(parts) >= 3 and parts[0] == "TEXT":
            author, message = parts[1], parts[2]
            if author != self.username or "[SYSTEM]" in message:
                self.add_message(f"{author}: {message}")

    def rename(self):
        new_name = self.name_entry.get().strip()
        if new_name and new_name != self.username:
            old_name = self.username
            self.username = new_name
            notice = f"TEXT@{self.username}@[SYSTEM] {old_name} змінив(ла) ім’я на {new_name}\n"
            try:
                self.sock.sendall(notice.encode("utf-8"))
                self.add_message(f"[СИСТЕМА] Ви змінили ім’я на {new_name}")
            except:
                self.add_message("[Помилка] Не вдалося надіслати повідомлення про зміну імені.")


win = MainWindow()
win.mainloop()

