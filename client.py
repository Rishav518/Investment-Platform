import csv
import sqlite3
import tkinter as tk
import requests
from tkinter import ttk
from tkinter import *
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


#Connection to server.py file
SERVER_URL = "http://localhost:5000"

# create a database connection
conn = sqlite3.connect('user_accounts.db')
c = conn.cursor()

#creating Window for App
windowlogin = tk.Tk()
windowlogin.geometry("500x500")
windowlogin.configure(bg='#381975')
windowlogin.title("Investment Trading Platform")



#Function to open a new account
def open_account():

    # create a custom dialog box
    dialog = tk.Toplevel(windowlogin)
    dialog.title("Open Account")
    dialog.geometry("300x200")
    dialog.configure(bg='#381975')

    # add name and balance labels and entries
    name_label = tk.Label(dialog, text="Name:", bg='#381975', fg='white')
    name_label.pack()

    name_entry = tk.Entry(dialog, bg='#471e96', foreground="white")
    name_entry.pack()

    balance_label = tk.Label(dialog, text="Initial Balance:", bg='#381975', fg='white')
    balance_label.pack()

    balance_entry = tk.Entry(dialog, bg='#471e96', foreground="white")
    balance_entry.pack()

    # add submit button
    submit_button = tk.Button(dialog, text="Submit",
                              command=lambda: create_account(name_entry.get(), balance_entry.get()),  bg='#381975', fg='white')
    submit_button.pack(pady=4)

    # function to create account
    def create_account(name, balance):
        if name and balance:
            data = {"name": name, "balance": balance}
            response = requests.post(f"{SERVER_URL}/accounts", json=data)

            if response.status_code == 200:
                # Retrieve the latest user's name and ID from the database
                conn = sqlite3.connect('user_Accounts.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name, id FROM accounts ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                conn.close()

                # Display the retrieved name and ID in a message box
                tk.messagebox.showinfo("Account Created", f"Your name is {result[0]} and your ID is {result[1]}.")
                dialog.destroy()
            else:
                tk.messagebox.showerror("Open Account", "Failed to create account.")
        else:
            tk.messagebox.showerror("Open Account", "Name and balance cannot be empty.")

#Function to display Gold, Silver and cryptocurrency prices with graph and buy or sell crypto
def invest():

    # create invest window
    invest_window = tk.Toplevel(windowlogin)
    invest_window.geometry("700x600")
    invest_window.configure(bg='#381975')

    # read csv file and get Gold and Silver prices from prices.csv file
    with open("prices.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "Gold":
                gold_price = row[1]
            if row[0] == "Silver":
                silver_price = row[1]


    # display Gold price label
    gold_label = tk.Label(invest_window, text=f"Gold Price: ${gold_price}", bg='#381975', foreground="white")
    gold_label.pack()
    # display Silver price label
    gold_label = tk.Label(invest_window, text=f"Silver Price: ${silver_price}", bg='#381975', foreground="white")
    gold_label.pack()

    # read data from crypto.csv file for cryptocurrency
    df = pd.read_csv("crypto.csv")

    # select cryptocurrency label and dropdown
    crypto_label = tk.Label(invest_window, text="Select Cryptocurrency:", bg='#381975', foreground="white")
    crypto_label.pack()

    crypto_var = tk.StringVar(invest_window)
    crypto_dropdown = tk.OptionMenu(invest_window, crypto_var, *df["Name"])
    # Se the background color of Options Menu to green
    crypto_dropdown.config(bg="#471e96", fg="WHITE")

    # Set the background color of Displayed Options to Red
    crypto_dropdown["menu"].config(bg="#381975", fg='white')
    crypto_dropdown.pack()


    # buy or sell radio buttons
    action_var = tk.StringVar(invest_window, "Buy")

    buy_radio = tk.Radiobutton(invest_window, text="Buy", variable=action_var, value="Buy", bg='#381975', foreground="white", selectcolor='#381975')
    buy_radio.pack()

    sell_radio = tk.Radiobutton(invest_window, text="Sell", variable=action_var, value="Sell", bg='#381975', foreground="white", selectcolor='#381975')
    sell_radio.pack()

    # amount label and entry
    amount_label = tk.Label(invest_window, text="Enter Amount:", bg='#381975', foreground="white")
    amount_label.pack()

    amount_entry = tk.Entry(invest_window, bg='#471e96', foreground="white")
    amount_entry.pack(pady=3)

    # submit button
    submit_button = tk.Button(invest_window, text="Submit", command=lambda: submit_transaction(crypto_var.get(), float(amount_entry.get()), action_var.get()), bg='#381975', foreground="white")
    submit_button.pack()

    # plot graph of cryptocurrency name and price
    fig = Figure(figsize=(5, 7), dpi=100, facecolor='#381975')
    ax = fig.add_subplot(111, facecolor='#381975')
    x = df["Name"]
    y = df["Cost"]
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    ax.bar(x, y, color=colors)
    ax.set_xlabel("Cryptocurrency").set_color('white')
    ax.set_ylabel("Price").set_color('white')
    ax.set_title("Cryptocurrency Prices").set_color('white')
    ax.legend(["Price"])
    ax.set_facecolor("#381975")
    ax.tick_params(colors='white', which='both')
    canvas = FigureCanvasTkAgg(fig, master=invest_window)
    canvas.draw()
    canvas.get_tk_widget().pack()


    # function to submit transaction and store in database
    def submit_transaction(crypto_name, amount, action):
        # connect to database
        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()

        # create table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      crypto_name TEXT,
                      amount REAL,
                      action TEXT)
                      ''')

        # insert transaction into table
        c.execute("INSERT INTO transactions (crypto_name, amount, action) VALUES (?, ?, ?)", (crypto_name, amount, action))
        conn.commit()

        # close database connection
        conn.close()

        # display message confirming transaction
        message = f"{action} {amount} {crypto_name} successfully."
        tk.messagebox.showinfo("Transaction", message)


def view_portfolio():
    # create view_portfolio window
    view_window = tk.Toplevel(windowlogin)
    view_window.geometry("800x400")
    view_window.title("View Portfolio")
    view_window.configure(bg='#381975')
    # create header label
    header_label = tk.Label(view_window, text="Transaction History", font=("Arial", 20, "bold"), background='#381975', foreground='white')
    header_label.pack(pady=5, padx=5)

    # create treeview to display data
    treeview = tk.ttk.Treeview(view_window, columns=("crypto_name", "amount", "action"))
    treeview.heading("crypto_name", text="Cryptocurrency")
    treeview.heading("amount", text="Amount")
    treeview.heading("action", text="Action")
    treeview.pack()

    # connect to database and fetch data
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    # add data to treeview
    for row in data:
        treeview.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3]))

    # add some padding to the treeview
    style = tk.ttk.Style()
    style.configure("Treeview", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"), bg='#381975')


def money_in_out():
    # create money window
    money_window = tk.Toplevel(windowlogin)
    money_window.geometry("500x500")
    # set background color
    money_window.configure(bg='#381975')

    # add or withdraw label and radio buttons
    action_label = tk.Label(money_window, text="Select an action:", bg='#381975', fg='white')
    action_label.pack()

    action_var = tk.StringVar(money_window, "Add")

    add_radio = tk.Radiobutton(money_window, text="Add", variable=action_var, value="Add",  bg='#381975', foreground="white", selectcolor='#381975')
    add_radio.pack()

    withdraw_radio = tk.Radiobutton(money_window, text="Withdraw", variable=action_var, value="Withdraw",  bg='#381975', foreground="white", selectcolor='#381975')
    withdraw_radio.pack()

    # money label and entry
    money_label = tk.Label(money_window, text="Enter Amount:",  bg='#381975', foreground="white")
    money_label.pack()

    money_entry = tk.Entry(money_window, bg='#471e96', foreground="white")
    money_entry.pack()

    # user id label and entry
    user_id_label = tk.Label(money_window, text="Enter User ID:",  bg='#381975', foreground="white")
    user_id_label.pack()

    user_id_entry = tk.Entry(money_window, bg='#471e96', foreground="white")
    user_id_entry.pack()

    # submit button
    submit_button = tk.Button(money_window, text="Submit", command=lambda: update_balance(action_var.get(), float(money_entry.get()),
                                                                                          int(user_id_entry.get())), bg='#471e96', foreground="white")
    submit_button.pack(pady=4)




def update_balance(action, amount, user_id):
    conn = sqlite3.connect("user_accounts.db")
    c = conn.cursor()

    # check if user exists
    c.execute("SELECT balance FROM accounts WHERE id=?", (user_id,))
    user_balance = c.fetchone()

    if user_balance:
        # update balance based on action
        if action == "Add":
            new_balance = user_balance[0] + amount
        elif action == "Withdraw":
            new_balance = user_balance[0] - amount
            if new_balance < 0:
                tk.messagebox.showerror("Error", "Insufficient funds.")
                return

        c.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, user_id))
        conn.commit()
        tk.messagebox.showinfo("Success", f"Transaction successful. New balance: {new_balance}")
    else:
        tk.messagebox.showerror("Error", "User not found.")

    conn.close()


def homepage():
    # creating Window for App
    window = tk.Tk()
    window.geometry("500x500")
    window.configure(bg='#381975')
    window.title("Investment Trading Platform")

    id = enter_user_id
    def showbalance():
        # Connect to the database
        conn = sqlite3.connect('user_accounts.db')
        cursor = conn.cursor()

        # Retrieve the balance for the given ID
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (id,))
        result = cursor.fetchone()

        # Check if the ID exists in the database
        if result is None:
            print("ID not found")
            balance_label.config(text="ID not found")
        else:
            # Update the label with the balance
            balance_label.config(text=f"Balance: ${result[0]}")

        # Close the database connection
        conn.close()

        # Schedule the next update in 5 seconds
        balance_label.after(5000, showbalance)

    def logout():
        window.destroy()

    # Main Menu
    username_label = tk.Label(window, text=f"Welcome, {enter_name}",foreground="white", background="#381975", font='Helvetica 18 bold')
    username_label.pack(pady=5)
    user_id_label = tk.Label(window, text=f"ID: {enter_user_id}", foreground="white", background="#381975")
    user_id_label.pack()
    # Create a label widget to display the balance
    balance_label = tk.Label(window, text="", foreground="white", background="#381975")
    # Add the label to the window
    balance_label.pack()
    # Start the periodic updates
    showbalance()
    invest_button = tk.Button(window, text="Invest", command=invest, foreground="white", background="#374151",
                              activebackground="#c2c2c2", activeforeground="white", borderwidth=1, padx=4)
    view_portfolio_button = tk.Button(window, text="View Portfolio", command=view_portfolio, foreground="white",
                                      background="#374151", activebackground="#c2c2c2", activeforeground="white",
                                      borderwidth=1, padx=4)
    money_in_out_button = tk.Button(window, text="Money In/Out", command=money_in_out, foreground="white",
                                    background="#374151", activebackground="#c2c2c2", activeforeground="white",
                                    borderwidth=1, padx=4)
    logout_button = tk.Button(window, text="Logout", command=logout, foreground="white",
                                    background="#374151", activebackground="#c2c2c2", activeforeground="white",
                                    borderwidth=1, padx=4)

    invest_button.pack(pady=5)
    view_portfolio_button.pack(pady=5)
    money_in_out_button.pack(pady=5)
    logout_button.pack(pady=5)


#function for user login with name and id
def login():
    dialog = tk.Toplevel(windowlogin)
    dialog.title("Login")
    dialog.geometry("300x200")
    dialog.configure(bg='#381975')
    # add name and balance labels and entries
    name_entry_label = tk.Label(dialog, text="Name:", bg='#381975', fg='white')
    name_entry = tk.Entry(dialog, bg='#471e96', foreground="white")
    id_entry_label = tk.Label(dialog, text="User ID:", bg='#381975', fg='white')
    id_entry = tk.Entry(dialog, bg='#471e96', foreground="white")

    #Check the enteries are valid or not
    def checkCredentials():
        # create a custom dialog box
        global enter_name
        global enter_user_id
        # Create a connection to the SQLite database
        conn = sqlite3.connect('user_accounts.db')

        # Create a cursor object to execute SQL queries
        c = conn.cursor()

        # Get the user's name and ID from the entry widgets
        enter_name = name_entry.get()
        enter_user_id = id_entry.get()

        # Execute a SELECT query to check if the user exists in the database
        c.execute("SELECT * FROM accounts WHERE name=? AND id=?", (enter_name, enter_user_id))

        # Fetch the result of the query
        result = c.fetchone()

        # If the query returns a result, call the homepage function
        if result:
            homepage()
        else:
            # If the query doesn't return a result, display an error message
            tk.messagebox.showerror("Open Account", "Invalid Credentials")

        # Close the cursor and the connection to the database
        c.close()
        conn.close()
        dialog.destroy()

    # add login button
    login_button = tk.Button(dialog, text="Login", bg='#381975', command=checkCredentials, fg='white')
    name_entry_label.pack()
    name_entry.pack()
    id_entry_label.pack()
    id_entry.pack()
    login_button.pack(pady=4)


#Adding HomePage Image
img = Image.open("images/home.png")
img = img.resize((200, 200), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(img)
label = tk.Label(windowlogin, image=photo, bg='#381975')
label.pack()

#Sign Up and Sign In buttons
open_account = tk.Button(windowlogin, command=open_account, text="Sign Up", foreground="white", background="#374151", activebackground="#c2c2c2", activeforeground="white", borderwidth=1, padx=4)
login_button = tk.Button(windowlogin,command=login, text="Sign In", foreground="white", background="#374151", activebackground="#c2c2c2", activeforeground="white", borderwidth=1, padx=4)
open_account.pack(pady=10)
login_button.pack(pady=10)


windowlogin.mainloop()