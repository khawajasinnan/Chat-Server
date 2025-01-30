import socket
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, font
from ttkthemes import ThemedTk
import threading
from datetime import datetime

EMOJI_KEY = {
    'A': '😊', 'B': '😂', 'C': '😍', 'D': '😎', 'E': '😉',
    'F': '😇', 'G': '😒', 'H': '😜', 'I': '😋', 'J': '😟',
    'K': '😕', 'L': '😬', 'M': '😱', 'N': '😅', 'O': '😆',
    'P': '😗', 'Q': '😛', 'R': '😪', 'S': '😭', 'T': '😐',
    'U': '😘', 'V': '😠', 'W': '😡', 'X': '😢', 'Y': '😝',
    'Z': '😷', ' ': '😶', '.': '😴', ',': '🥺',
    '0': '🎯', '1': '🎨', '2': '🎭', '3': '🎪', '4': '🎈',
    '5': '🎄', '6': '🎅', '7': '🎉', '8': '🎎', '9': '🎌',
    '!': '🌟', '@': '🌙', '#': '🌛', '$': '🌝', '%': '🌞',
    '^': '🌺', '&': '🌹', '*': '🌷', '(': '🌸', ')': '🌼',
    '-': '🍀', '_': '🍁', '+': '🍂', '=': '🍃', '/': '🍄',
    '?': '💫', '<': '💨', '>': '💦', '[': '💡', ']': '💢',
    '{': '💣', '}': '💥', '|': '💫', '\\': '💬', "'": '💭',
    '"': '💮', ';': '💯', ':': '💰', '`': '💲', '~': '💳'
}

RANDOM_EMOJIS = ['⭐', '🌙', '☀️', '⚡', '🌈', '🌪️', '❄️', '☁️']
REVERSE_EMOJI_KEY = {v: k for k, v in EMOJI_KEY.items()}

def encrypt_message(message):
    encrypted = ""
    block_count = 0
    steps = []
    
    for char in message.upper():
        if char in EMOJI_KEY:
            emoji = EMOJI_KEY[char]
            encrypted += emoji
            steps.append(f"'{char}' → '{emoji}'")
            block_count += 1
            if block_count % 5 == 0:
                random_emoji = random.choice(RANDOM_EMOJIS)
                encrypted += random_emoji
                steps.append(f"Block separator: '{random_emoji}'")
    
    return encrypted, steps

def decrypt_message(encrypted):
    decrypted = ""
    steps = []
    chars = list(encrypted)
    i = 0
    
    while i < len(chars):
        if chars[i] in REVERSE_EMOJI_KEY:
            char = REVERSE_EMOJI_KEY[chars[i]]
            decrypted += char
            steps.append(f"'{chars[i]}' → '{char}'")
            i += 1
        elif chars[i] in RANDOM_EMOJIS:
            steps.append(f"Removed separator: '{chars[i]}'")
            i += 1
        else:
            i += 1
            
    return decrypted, steps

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Emoji Chat Client ✨")
        self.root.geometry("1000x700")
        
        # Apply theme
        self.style = ttk.Style()
        self.style.configure("Emoji.TFrame", background="#2C3E50")
        self.style.configure("Chat.TFrame", background="#ECF0F1")
        self.style.configure("Status.TLabel", 
                           font=("Helvetica", 10),
                           background="#2C3E50",
                           foreground="#ECF0F1")
        
        # Main container
        self.main_frame = ttk.Frame(root, style="Emoji.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Emoji palette frame
        self.create_emoji_palette()
        
        # Chat area
        self.chat_frame = ttk.Frame(self.main_frame, style="Chat.TFrame")
        self.chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Custom font for chat
        self.chat_font = font.Font(family="Helvetica", size=12)
        
        # Chat history display with custom tags
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=self.chat_font,
            background="#FFFFFF",
            foreground="#2C3E50"
        )
        self.chat_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Configure tags for different message types
        self.chat_display.tag_configure("system", foreground="#95A5A6")
        self.chat_display.tag_configure("encryption", foreground="#27AE60")
        self.chat_display.tag_configure("decryption", foreground="#8E44AD")
        self.chat_display.tag_configure("you", foreground="#2980B9")
        self.chat_display.tag_configure("server", foreground="#C0392B")
        self.chat_display.tag_configure("arrow", foreground="#7F8C8D")
        
        # Message input area with modern styling
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.message_input = ttk.Entry(
            self.input_frame,
            font=self.chat_font
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.send_button = ttk.Button(
            self.input_frame,
            text="Send 📤",
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)
        
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame, style="Emoji.TFrame")
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="🔴 Disconnected",
            style="Status.TLabel"
        )
        self.status_label.pack(pady=5)
        
        # Socket setup
        self.client_socket = None
        self.connected = False
        
        # Start connection
        self.connect_to_server()

    def create_emoji_palette(self):
        self.emoji_frame = ttk.Frame(self.main_frame)
        self.emoji_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.emoji_canvas = tk.Canvas(self.emoji_frame, height=100)
        self.emoji_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        scrollbar = ttk.Scrollbar(self.emoji_frame, orient=tk.HORIZONTAL, 
                                command=self.emoji_canvas.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.emoji_canvas.configure(xscrollcommand=scrollbar.set)
        
        self.emoji_buttons = ttk.Frame(self.emoji_canvas)
        self.emoji_canvas.create_window((0, 0), window=self.emoji_buttons, 
                                      anchor=tk.NW)
        
        for char, emoji in EMOJI_KEY.items():
            btn = ttk.Button(self.emoji_buttons, text=f"{emoji}", 
                           command=lambda e=emoji: self.insert_emoji(e))
            btn.pack(side=tk.LEFT, padx=2)
        
        self.emoji_buttons.update_idletasks()
        self.emoji_canvas.configure(scrollregion=self.emoji_canvas.bbox("all"))

    def insert_emoji(self, emoji):
        current = self.message_input.get()
        cursor_pos = self.message_input.index(tk.INSERT)
        new_text = current[:cursor_pos] + emoji + current[cursor_pos:]
        self.message_input.delete(0, tk.END)
        self.message_input.insert(0, new_text)

    def append_message(self, sender, message, tag=None):
        self.chat_display.configure(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if tag == "arrow":
            self.chat_display.insert(tk.END, f"{message}\n", tag)
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n", 
                                   tag if tag else sender.lower())
        
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 12345))
            self.connected = True
            self.status_label.configure(text="🟢 Connected")
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.append_message("System", "Connected to server", "system")
        except Exception as e:
            self.append_message("System", f"Connection failed: {str(e)}", "system")

    def send_message(self):
        if not self.connected:
            self.append_message("System", "Not connected to server", "system")
            return
            
        message = self.message_input.get().strip()
        if message:
            self.message_input.delete(0, tk.END)
            self.append_message("You", message, "you")
            
            encrypted, steps = encrypt_message(message)
            self.append_message("Encryption", "Converting message to emojis:", "encryption")
            for step in steps:
                self.append_message("→", step, "arrow")
            self.append_message("Encryption", f"Final: {encrypted}", "encryption")
            
            try:
                self.client_socket.send(encrypted.encode('utf-8'))
            except Exception as e:
                self.append_message("System", f"Failed to send message: {str(e)}", "system")

    def receive_messages(self):
        while self.connected:
            try:
                encrypted_response = self.client_socket.recv(4096).decode('utf-8')
                if not encrypted_response:
                    break
                
                self.append_message("Received", f"Encrypted message: {encrypted_response}", "system")
                decrypted, steps = decrypt_message(encrypted_response)
                self.append_message("Decryption", "Converting emojis to text:", "decryption")
                for step in steps:
                    self.append_message("→", step, "arrow")
                self.append_message("Server", decrypted, "server")
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        
        self.connected = False
        self.status_label.config(text="🔴 Disconnected")

    def on_closing(self):
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()