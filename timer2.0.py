import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import os
import winsound

REMINDER_FILE = "reminder.txt"
REMINDER_FOLDER = "reminders"
timer_window = None

def countdown(countdown_frame, reminder_text, countdown_text, reminder_time, reminder_datetime, hurry_up_custom_text):
    countdown_var = tk.StringVar()
    countdown_frame = tk.Frame(timer_window)
    countdown_frame.pack()
    countdown_label = tk.Label(countdown_frame, textvariable=countdown_var, font=("Helvetica", 20))
    countdown_label.pack()

    progress_bar = ttk.Progressbar(countdown_frame, length=200, mode='determinate')
    progress_bar.pack(pady=10)

    hurry_up_text = tk.StringVar()
    hurry_up_label = tk.Label(countdown_frame, textvariable=hurry_up_text, font=("Helvetica", 12))
    hurry_up_label.pack(pady=5)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Horizontal.TProgressbar",
                    thickness=20,
                    troughcolor='#EAEAEA',
                    troughrelief='flat',
                    troughborderwidth=0,
                    bordercolor='#EAEAEA',
                    lightcolor='#FFD700',
                    darkcolor='#FFA500')

    initial_reminder_time = reminder_time  # Store the initial reminder time

    def update_countdown():
        remaining_time = int((reminder_datetime - datetime.datetime.now()).total_seconds())
        if remaining_time >= 0:
            countdown_var.set(countdown_text.format(str(datetime.timedelta(seconds=remaining_time)), reminder_text))
            progress = ((initial_reminder_time - remaining_time) / initial_reminder_time) * 100
            progress_bar['value'] = progress
            hurry_up_text.set(hurry_up_custom_text if hurry_up_custom_text 
                              else (reminder_text + " is hard. Please do not fuck up :)"))
            countdown_frame.after(1000, update_countdown)
        else:
            finish_countdown()
    def finish_countdown():
        global timer_window
        countdown_var.set("Time's up! " + reminder_text)
        
        # Play sound when time's up
        winsound.Beep(2500, 1000)  # frequency, duration
        if not timer_window.winfo_children():  # if there are no other frames in timer_window
            timer_window.destroy()  # destroy timer_window
            timer_window = None  # reset timer_window to None

        # Wait for 10 seconds and then exit the countdown window
        countdown_frame.after(10000, countdown_frame.destroy)

    update_countdown()

    button_close = tk.Button(countdown_frame, text="Close This Timer", command=countdown_frame.destroy)
    button_close.pack()

def save_reminder_time(remaining_time):
    with open(REMINDER_FILE, "w") as file:
        file.write(str(remaining_time))

def delete_reminder():
    # Get the selected filename from the list box
    selected_file = listbox.get(listbox.curselection())
    # Delete the reminder file
    reminder_file = f"{REMINDER_FOLDER}/{selected_file}"
    try:
        os.remove(reminder_file)
        # Refresh the list box with updated reminder files
        refresh_reminder_list()
        messagebox.showinfo("Delete Reminder", "Reminder deleted successfully.")
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "Selected reminder file not found.")

def set_reminder():
    global timer_window
    reminder_text = entry.get()
    reminder_date_str = entry_date.get()
    reminder_time_str = entry_time.get()
    hurry_up_custom_text = entry_hurry_up.get()  # get custom hurry up text

    if timer_window is None or not timer_window.winfo_exists():
        timer_window = tk.Toplevel(root)
        timer_window.title("All Timers")


    try:
        reminder_date = datetime.datetime.strptime(reminder_date_str, "%Y-%m-%d")
        reminder_time = datetime.datetime.strptime(reminder_time_str, "%H:%M:%S")
        reminder_datetime = datetime.datetime.combine(reminder_date.date(), reminder_time.time())
        current_datetime = datetime.datetime.now()
        time_difference = (reminder_datetime - current_datetime).total_seconds()

        if time_difference > 0:
            countdown_text = "Time remaining: {} to {}"
            countdown_frame = tk.Frame(timer_window)
            countdown_frame.pack(pady=10)
            countdown(countdown_frame, reminder_text, countdown_text, int(time_difference), reminder_datetime, hurry_up_custom_text)
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

            # Refresh the list box with updated reminder files
            refresh_reminder_list()

            messagebox.showinfo("Save Reminder", "Reminder text saved successfully.")
        else:
            messagebox.showerror("Invalid Reminder Text", "Please enter a reminder text.")
    except ValueError:
        messagebox.showerror("Invalid Date or Time", "Please enter the date and time in the correct format.")

def refresh_reminder_list():
    # Clear the list box
    listbox.delete(0, tk.END)

    # Populate the list box with files in the reminders folder
    if os.path.exists(REMINDER_FOLDER):
        for filename in os.listdir(REMINDER_FOLDER):
            listbox.insert(tk.END, filename)

def resume_countdown(event):
    global timer_window
    if timer_window is None or not timer_window.winfo_exists():
        timer_window = tk.Toplevel(root)
        timer_window.title("All Timers")

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
            # Start the countdown with the remaining time
            countdown_text = "Time remaining: {} to {}"
            countdown_frame = tk.Frame(timer_window)
            countdown_frame.pack(pady=10)
            countdown(countdown_frame, reminder_text, countdown_text, remaining_time, reminder_datetime, "")
        else:
            messagebox.showerror("Invalid Reminder File", "Invalid reminder file format or the reminder time has already passed.")
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "Selected reminder file not found.")

root = tk.Tk()
root.title("Aled Timer")

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

label_hurry_up = tk.Label(root, text="Set A Whatever:")
label_hurry_up.pack()

entry_hurry_up = tk.Entry(root)
entry_hurry_up.pack()

button_set = tk.Button(root, text="Set Reminder", command=set_reminder)
button_set.pack()

button_delete = tk.Button(root, text="Delete Reminder", command=delete_reminder)
button_delete.pack()

listbox = tk.Listbox(root)
listbox.pack()
listbox.bind("<Double-Button-1>", resume_countdown)

# Populate the list box with files in the reminders folder
if os.path.exists(REMINDER_FOLDER):
    for filename in os.listdir(REMINDER_FOLDER):
        listbox.insert(tk.END, filename)

button_save = tk.Button(root, text="Save Reminder Text", command=save_reminder_text)
button_save.pack()

countdown_frame = tk.Frame(root)
countdown_frame.pack()

root.mainloop()
