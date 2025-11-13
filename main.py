import sys
import tkinter as tk
from client import Client

if len(sys.argv)<3:
    print("Usage: python main.py SERVER_IP SERVER_PORT")
    sys.exit(1)

SERVER, PORT = sys.argv[1], int(sys.argv[2])

root = tk.Tk()
root.title("Counter-Strike Tkinter")
client = Client(root, SERVER, PORT)
root.mainloop()
