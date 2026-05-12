import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Function to Save Records you created in the database

def save_record():

    agency = agency_entry.get()
    officer_in_charge = officer_entry.get()
    phone_model = model_entry.get()
    phone_number = phone_number_entry.get()
    digits_number = digits_entry.get()
    work = work_entry.get()
    fault = fault_entry.get()
    config = config_entry.get()
    install = install_entry.get()
    status = status_entry.get()
    customer = customer_entry.get()

    new_record = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Agency": agency,
        "Officer_in_charge": officer_in_charge,
        "Phone_Model": phone_model,
        "Phone_number": phone_number,
        "Digits_number": digits_number,
        "Work_Type": work,
        "Fault": fault,
        "Config_File": config,
        "New_Install": install,
        "Status": status,
        "Customer_Name": customer
    }

    df = pd.read_csv("phone_data.csv")

    df = pd.concat([df, pd.DataFrame([new_record])])

    df.to_csv("phone_data.csv", index=False)

    messagebox.showinfo("Success","Record Saved Successfully")


# Create Window

window = tk.Tk()

window.title("IP Phones Management System")

window.geometry("500x600")


tk.Label(window,text="Agency").pack()
agency_entry = tk.Entry(window)
agency_entry.pack()

tk.Label(window,text="Officer Name").pack()
officer_entry = tk.Entry(window)
officer_entry.pack()

tk.Label(window,text="Phone Model (7910/7950/8910)").pack()
model_entry = tk.Entry(window)
model_entry.pack()

tk.Label(window,text="Phone Number").pack()
phone_number_entry = tk.Entry(window)
phone_number_entry.pack()

tk.Label(window,text="Digits (5 or 6)").pack()
digits_entry = tk.Entry(window)
digits_entry.pack()

tk.Label(window,text="Work Type").pack()
work_entry = tk.Entry(window)
work_entry.pack()

tk.Label(window,text="Fault Type").pack()
fault_entry = tk.Entry(window)
fault_entry.pack()

tk.Label(window,text="Configuration File Added (Yes/No)").pack()
config_entry = tk.Entry(window)
config_entry.pack()

tk.Label(window,text="New Phone Installed (Yes/No)").pack()
install_entry = tk.Entry(window)
install_entry.pack()

tk.Label(window,text="Status (Working/Not Working)").pack()
status_entry = tk.Entry(window)
status_entry.pack()

tk.Label(window,text="Customer Name").pack()
customer_entry = tk.Entry(window)
customer_entry.pack()


tk.Button(window,text="Save Record",command=save_record).pack(pady=20)


window.mainloop()