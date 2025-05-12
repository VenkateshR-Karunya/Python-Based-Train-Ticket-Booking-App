import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# PostgreSQL Initializing
def get_db_connection():
    return psycopg2.connect(
        dbname="oidfd",
        user="postgres",
        password="leave",
        host="localhost",
        port="5432"
    )

# Bookings App Function
def open_booking_window():
    login_window.destroy()

    root = tk.Tk()
    root.title("Railway Ticket Booking System")
    root.geometry("1200x600")

    def book_ticket():
        name = name_entry.get()
        age = age_entry.get()
        gender = gender_var.get()
        train = train_var.get()
        from_loc = from_entry.get()
        to_loc = to_entry.get()

        if not name or not age or not gender or not train or not from_loc or not to_loc:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO bookings (name, age, gender, train, source, destination) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, age, gender, train, from_loc, to_loc)
            )
            conn.commit()
            cur.close()
            conn.close()
            update_booking_list()
            clear_fields()
            messagebox.showinfo("Success", "Ticket booked successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def clear_fields():
        name_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        gender_var.set(None)
        train_var.set(trains[0])
        from_entry.delete(0, tk.END)
        to_entry.delete(0, tk.END)

    def update_booking_list():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT name, age, gender, train, source, destination FROM bookings")
            records = cur.fetchall()
            cur.close()
            conn.close()

            booking_list.delete(*booking_list.get_children())
            for row in records:
                booking_list.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def cancel_ticket():
        selected_item = booking_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a ticket to cancel.")
            return

        confirm = messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the selected ticket?")
        if not confirm:
            return

        try:
            item = booking_list.item(selected_item)
            name, age, gender, train, source, destination = item['values']

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM bookings
                WHERE ctid IN (
                    SELECT ctid FROM bookings 
                    WHERE name = %s AND age = %s AND gender = %s AND train = %s AND source = %s AND destination = %s
                    LIMIT 1
                )
            """, (name, age, gender, train, source, destination))

            conn.commit()
            cur.close()
            conn.close()

            update_booking_list()
            messagebox.showinfo("Cancelled", f"Ticket for '{name}' has been cancelled.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Label(root, text="Passenger Name:").place(x=30, y=30)
    name_entry = tk.Entry(root)
    name_entry.place(x=150, y=30)

    tk.Label(root, text="Age:").place(x=30, y=70)
    age_entry = tk.Entry(root)
    age_entry.place(x=150, y=70)

    tk.Label(root, text="Gender:").place(x=30, y=110)
    gender_var = tk.StringVar()
    tk.Radiobutton(root, text="Male", variable=gender_var, value="Male").place(x=150, y=110)
    tk.Radiobutton(root, text="Female", variable=gender_var, value="Female").place(x=220, y=110)

    tk.Label(root, text="Select Train:").place(x=30, y=150)
    trains = ["Rajdhani Express", "Shatabdi Express", "Duronto Express", "Garib Rath", "Intercity Express"]
    train_var = tk.StringVar(value=trains[0])
    train_menu = ttk.Combobox(root, textvariable=train_var, values=trains, state="readonly")
    train_menu.place(x=150, y=150)

    tk.Label(root, text="From:").place(x=30, y=190)
    from_entry = tk.Entry(root)
    from_entry.place(x=150, y=190)

    tk.Label(root, text="To:").place(x=30, y=230)
    to_entry = tk.Entry(root)
    to_entry.place(x=150, y=230)

    tk.Button(root, text="Book Ticket", command=book_ticket, bg="green", fg="white").place(x=150, y=270)
    tk.Button(root, text="Clear", command=clear_fields).place(x=250, y=270)
    tk.Button(root, text="Cancel Ticket", command=cancel_ticket, bg="red", fg="white").place(x=340, y=270)

    columns = ("Name", "Age", "Gender", "Train", "From", "To")
    booking_list = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        booking_list.heading(col, text=col)
        booking_list.column(col, anchor=tk.CENTER)

    booking_list.place(x=10, y=320, width=1200, height=200)

    update_booking_list()
    root.mainloop()

# Login Window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")
# Credentials - Only one for now
USERNAME = "admin"
PASSWORD = "1234"

def check_login():
    user = user_entry.get()
    pwd = pass_entry.get()

    if user == USERNAME and pwd == PASSWORD:
        open_booking_window()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

tk.Label(login_window, text="Username:").pack(pady=10)
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password:").pack(pady=10)
pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()

tk.Button(login_window, text="Login", command=check_login, bg="blue", fg="white").pack(pady=20)

login_window.mainloop()
