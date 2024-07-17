import tkinter as tk
from tkinter import messagebox

# Create the main application window
root = tk.Tk()
root.title("Simple GUI Example")

# Create a label
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=10)

# Create an entry widget
entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Function to show a message box with the entry content
def show_message():
    user_input = entry.get()
    messagebox.showinfo("Message", f"You entered: {user_input}")

# Create a button that triggers the show_message function
button = tk.Button(root, text="Show Message", command=show_message)
button.pack(pady=10)

# Run the application
root.mainloop()
