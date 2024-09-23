import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Fruit List Display with Filtering")
root.geometry("400x300")

# Fruit list
fruits = ['Apple', 'Banana', 'Orange', 'Mango', 'Pineapple', 'Arapes', 'Strawberry', 'Kiwi', 'Blueberry', 'Peach']

# Function to update the listbox with filtered options
def update_listbox(event):
    typed_text = entry.get().lower()
    
    # Filter the fruit list
    filtered_fruits = [fruit for fruit in fruits if typed_text in fruit.lower()]
    
    # Clear the current listbox
    listbox.delete(0, tk.END)
    
    # Add the filtered fruits to the listbox
    for fruit in filtered_fruits:
        listbox.insert(tk.END, fruit)

# Create the input box (Entry widget)
entry_label = tk.Label(root, text="Type to filter fruits:")
entry_label.pack(pady=5)

entry = tk.Entry(root)
entry.pack(pady=5)

# Create the frame to hold the Listbox and Scrollbar
frame = tk.Frame(root)
frame.pack(pady=10)

# Create the Listbox and Scrollbar
listbox = tk.Listbox(frame, height=10, width=30)
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Pack the Listbox and Scrollbar
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Populate the Listbox with the initial fruit list
for fruit in fruits:
    listbox.insert(tk.END, fruit)

# Bind key release event to filter the listbox options
entry.bind("<KeyRelease>", update_listbox)

# Run the Tkinter event loop
root.mainloop()
