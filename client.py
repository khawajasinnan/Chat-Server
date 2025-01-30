import socket
import random

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
    print(f"\nEncrypting: {message}")
    encrypted = ""
    block_count = 0
    
    for char in message.upper():
        if char in EMOJI_KEY:
            emoji = EMOJI_KEY[char]
            encrypted += emoji
            print(f"Char {char} -> Emoji {emoji}")
            block_count += 1
            if block_count % 5 == 0:
                random_emoji = random.choice(RANDOM_EMOJIS)
                encrypted += random_emoji
                print(f"Added block separator: {random_emoji}")
    
    print(f"Final encrypted: {encrypted}")
    return encrypted

def decrypt_message(encrypted):
    print(f"\nDecrypting: {encrypted}")
    decrypted = ""
    chars = list(encrypted)
    i = 0
    
    while i < len(chars):
        if chars[i] in REVERSE_EMOJI_KEY:
            char = REVERSE_EMOJI_KEY[chars[i]]
            decrypted += char
            print(f"Emoji {chars[i]} -> Char {char}")
            i += 1
        elif chars[i] in RANDOM_EMOJIS:
            print(f"Skipping separator: {chars[i]}")
            i += 1
        else:
            i += 1
            
    print(f"Final decrypted: {decrypted}")
    return decrypted

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 12345))
    
    test_message = "HELLO"
    print("\nTesting encryption:")
    test_encrypted = encrypt_message(test_message)
    print(f"Test decrypt: {decrypt_message(test_encrypted)}")
    
    try:
        while True:
            message = input("Enter message: ")
            encrypted = encrypt_message(message)
            print(f"Sending encrypted: {encrypted}")
            client.send(encrypted.encode('utf-8'))
            
            response = client.recv(4096).decode('utf-8')
            print(f"Received encrypted: {response}")
            decrypted = decrypt_message(response)
            print(f"Server response: {decrypted}")
            
    except KeyboardInterrupt:
        print("\nClosing connection...")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()