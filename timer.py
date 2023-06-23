import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import os

REMINDER_FILE = "reminder.txt"
REMINDER_FOLDER = "reminders"

def countdown(reminder_window, reminder_text, countdown_text, reminder_time):
    countdown_var = tk.StringVar()
    countdown_label = tk.Label(reminder_window, textvariable=countdown_var, font=("Helvetica", 20))
    countdown_label.pack()

    progress_bar = ttk.Progressbar(reminder_window, length=200, mode='determinate')
    progress_bar.pack(pady=10)

    hurry_up_text = tk.StringVar()
    hurry_up_label = tk.Label(reminder_window, textvariable=hurry_up_text, font=("Helvetica", 12))
    hurry_up_label.pack(pady=5)

    initial_reminder_time = reminder_time  # Store the initial reminder time

    def update_countdown():
        countdown_var.set(countdown_text.format(str(datetime.timedelta(seconds=reminder_time)), reminder_text))
        progress = (reminder_time / initial_reminder_time) * 100
        progress_bar['value'] = progress
        hurry_up_text.set(reminder_text + " is hard. Please do not fuck up :)")

    def finish_countdown():
        countdown_var.set("Time's up! " + reminder_text)
        # Wait for 10 seconds and then exit the countdown window
        reminder_window.after(10000, reminder_window.destroy)
        # Remove the reminder file after the countdown finishes
        remove_reminder_file()

    def update_and_schedule(remaining_time):
        nonlocal reminder_time
        reminder_time = remaining_time
        update_countdown()
        reminder_time -= 1
        if reminder_time >= 0:
            # Save the remaining time to the reminder file
            save_reminder_time(reminder_time)
            reminder_window.after(1000, update_and_schedule, reminder_time)
        else:
            finish_countdown()

    update_and_schedule(reminder_time)

def save_reminder_time(remaining_time):
    with open(REMINDER_FILE, "w") as file:
        file.write(str(remaining_time))

def remove_reminder_file():
    try:
        # Remove the reminder file
        os.remove(REMINDER_FILE)
    except FileNotFoundError:
        pass

def set_reminder():
    reminder_text = entry.get()
    reminder_date_str = entry_date.get()
    reminder_time_str = entry_time.get()

    try:
        reminder_date = datetime.datetime.strptime(reminder_date_str, "%Y-%m-%d")
        reminder_time = datetime.datetime.strptime(reminder_time_str, "%H:%M:%S")
        reminder_datetime = datetime.datetime.combine(reminder_date.date(), reminder_time.time())
        current_datetime = datetime.datetime.now()
        time_difference = (reminder_datetime - current_datetime).total_seconds()

        if time_difference > 0:
            countdown_text = "Time remaining: {} to {}"
            reminder_window = tk.Toplevel(root)
            countdown(reminder_window, reminder_text, countdown_text, int(time_difference))
            # Save the reminder details to the reminder file
            save_reminder_time(int(time_difference))
        else:
            messagebox.showerror("Invalid Reminder Time", "Please enter a future time.")
    except ValueError:
        messagebox.showerror("Invalid Date or Time", "Please enter the date and time in the correct format.")

def save_reminder_text():
    reminder_text = entry.get()
    reminder_date_str = entry_date.get()
    reminder_time_str = entry_time.get()
    
    try:
        reminder_date = datetime.datetime.strptime(reminder_date_str, "%Y-%m-%d")
        reminder_time = datetime.datetime.strptime(reminder_time_str, "%H:%M:%S")
        reminder_datetime = datetime.datetime.combine(reminder_date.date(), reminder_time.time())
        timestamp = reminder_datetime.strftime("%Y%m%d%H%M%S")

        if reminder_text:
            # Create the reminders folder if it doesn't exist
            if not os.path.exists(REMINDER_FOLDER):
                os.makedirs(REMINDER_FOLDER)
            
            # Generate a unique filename based on the reminder text
            filename = f"{REMINDER_FOLDER}/{reminder_text}.txt"
            with open(filename, "w") as file:
                file.write(reminder_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            
            messagebox.showinfo("Save Reminder", "Reminder text saved successfully.")
        else:
            messagebox.showerror("Invalid Reminder Text", "Please enter a reminder text.")
    except ValueError:
        messagebox.showerror("Invalid Date or Time", "Please enter the date and time in the correct format.")


def resume_countdown(event):
    # Get the selected filename from the list box
    selected_file = listbox.get(listbox.curselection())
    # Read the reminder file
    reminder_file = f"{REMINDER_FOLDER}/{selected_file}"
    try:
        with open(reminder_file, "r") as file:
            reminder_datetime_str = file.read()
        
        reminder_datetime = datetime.datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M:%S")
        current_datetime = datetime.datetime.now()
        remaining_time = int((reminder_datetime - current_datetime).total_seconds())
        if remaining_time > 0:
            reminder_text = os.path.splitext(selected_file)[0]
            # Remove the reminder file before resuming the countdown
            remove_reminder_file()
            # Start the countdown with the remaining time
            countdown_text = "Time remaining: {} to {}"
            reminder_window = tk.Toplevel(root)
            countdown(reminder_window, reminder_text, countdown_text, remaining_time)
        else:
            messagebox.showerror("Invalid Reminder File", "Invalid reminder file format or the reminder time has already passed.")
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "Selected reminder file not found.")

root = tk.Tk()

label = tk.Label(root, text="Enter reminder:")
label.pack()

entry = tk.Entry(root)
entry.pack()

label_date = tk.Label(root, text="Enter date (YYYY-MM-DD):")
label_date.pack()

entry_date = tk.Entry(root)
entry_date.pack()

label_time = tk.Label(root, text="Enter time (HH:MM:SS):")
label_time.pack()

entry_time = tk.Entry(root)
entry_time.pack()

button_set = tk.Button(root, text="Set Reminder", command=set_reminder)
button_set.pack()

listbox = tk.Listbox(root)
listbox.pack()

# Populate the list box with files in the reminders folder
if os.path.exists(REMINDER_FOLDER):
    for filename in os.listdir(REMINDER_FOLDER):
        listbox.insert(tk.END, filename)

button_save = tk.Button(root, text="Save Reminder Text", command=save_reminder_text)
button_save.pack()

# Bind double-click event on the list box to resume countdown
listbox.bind("<Double-Button-1>", resume_countdown)

root.mainloop()