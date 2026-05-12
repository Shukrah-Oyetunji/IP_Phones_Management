from flask import Flask, flash, render_template, request, redirect, session,send_file
import pandas as pd
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "galaxy_backbone_secret"  # Required for sessions

# Create CSV automatically if it doesn't exist
if not os.path.exists("phone_data.csv"):
    df = pd.DataFrame(columns=[
        "Date",
        "Ministry",
        "PhoneType",
        "Extension",
        "Action",
        "Fault",
        "Description",
        "Status",
        "Support Engineer",
        "Incident Time","Resolution Time","MTTR"
    ])
    df.to_csv("phone_data.csv", index=False)

if not os.path.exists("users.csv"):
    df_users = pd.DataFrame(columns=["Username", "Password"])
    df_users.to_csv("users.csv", index=False)


# DECORATOR FOR PROTECTED ROUTES
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- LOGIN PAGE ---------------- 
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        df_users = pd.read_csv("users.csv")
        # Check if username and password match any row in users.csv
        user_exists = ((df_users["Username"] == username) & (df_users["Password"] == password)).any()

        if user_exists:
            session["user"] = username
            return redirect("/actions")
        else:
            return render_template("login.html", error="Invalid credentials. Please try again.")

    return render_template("login.html")

# ---------------- SIGNUP PAGE ---------------- 
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
             return render_template("signup.html", error="Passwords do not match.")

        df_users = pd.read_csv("users.csv")
        
        if (df_users["Username"] == username).any():
            return render_template("signup.html", error="Username already exists.")

        # Add new user
        new_user = pd.DataFrame([{"Username": username, "Password": password}])
        new_user.to_csv("users.csv", mode='a', header=False, index=False)
        
        return redirect("/login")

    return render_template("signup.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

#  ACTION
@app.route("/actions")
@login_required
def actions():
    return render_template("actions.html")

# DASHBOARD PAGE
@app.route("/dashboard")
@login_required
def dashboard():

    try:
        df = pd.read_csv("phone_data.csv",dtype=str)
        print(df.head())  # DEBUG LINE

        data = df.to_dict(orient="records")

    except Exception as e:
        print("ERROR:", e)
        data = []

    return render_template("dashboard.html", data=data)

#  ---------------- View records ----------------
@app.route("/view_records")
@login_required
def view_records():
    import pandas as pd

    try:
        df = pd.read_csv("phone_data.csv", dtype=str)
    except:
        df = pd.DataFrame()

    return render_template(
        "view_records.html",
        data=df.to_dict(orient="records")
    )

# ---------------- SAVE RECORD ----------------
@app.route("/save", methods=["POST"])
@login_required
def save():
    from datetime import datetime
    import pandas as pd

    # Handle fault
    fault = request.form["fault"]
    if fault == "Others":
        fault = request.form.get("other_fault", "Others")

    # Get time inputs
    incident_time = request.form["incident_time"]
    resolution_time = request.form["resolution_time"]

    # Convert to datetime
    incident_dt = datetime.fromisoformat(incident_time)
    resolution_dt = datetime.fromisoformat(resolution_time)

    # VALIDATION (VERY IMPORTANT)
    if resolution_dt < incident_dt:
        flash("Resolution time cannot be before incident time!", "danger")
        return redirect("/dashboard")

    # Calculate MTTR
    time_diff = resolution_dt - incident_dt

    total_minutes = int(time_diff.total_seconds() / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    mttr = f"{hours} hrs {minutes} mins"

    # Prepare data
    data = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Ministry": request.form["ministry"],
        "PhoneType": request.form["phone"],
        "Extension": request.form["extension"],
        "Action": request.form["action"],
        "Fault": fault,
        "Description": request.form.get("description", ""),
        "Status": request.form["status"],
        "Support Engineer": request.form["tech"],
        "Incident Time": incident_time,
        "Resolution Time": resolution_time,
        "MTTR": mttr
    }

    #  Save to CSV
    df = pd.DataFrame([data])
    df.to_csv("phone_data.csv", mode='a', header=False, index=False)

    flash("Record saved successfully!", "success")
    return redirect("/dashboard")

# Edit Function

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    import pandas as pd

    df = pd.read_csv("phone_data.csv", dtype=str)  # FORCE data type as STRING

    if request.method == "POST":

        #  Get form values
        incident_time = request.form["incident_time"]
        resolution_time = request.form["resolution_time"]

        # Convert to datetime
        incident_dt = datetime.fromisoformat(incident_time)
        resolution_dt = datetime.fromisoformat(resolution_time)

        # Validate
        if resolution_dt < incident_dt:
            flash("Resolution time cannot be before incident time!", "danger")
            return redirect("/view_records")
          # Calculate MTTR
        time_diff = resolution_dt - incident_dt
        total_minutes = int(time_diff.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        mttr = f"{hours} hrs {minutes} mins"

        df.at[id, "Ministry"] = request.form["ministry"]
        df.at[id, "Phone Type"] = request.form["phone"]
        df.at[id, "Extension"] = request.form["extension"]
        df.at[id, "Action"] = request.form["action"]
        df.at[id, "Fault"] = request.form["fault"]
        df.at[id, "Status"] = request.form["status"]
        df.at[id, "Support Engineer"] = request.form["tech"]
        df.at[id, "Incident Time"] = incident_time
        df.at[id, "Resolution Time"] = resolution_time
        df.at[id, "MTTR"] = mttr
        # To save
        df.to_csv("phone_data.csv", index=False)
        flash("Record updated successfully!", "success")
        return redirect("/view_records")
    # For GET (To Load Record)
    record = df.iloc[id].to_dict()
    # Fix datetime format for input
    if "Incident Time" in record:
        record["Incident Time"] = record["Incident Time"].replace(" ", "T")
    if "Resolution Time" in record:
        record["Resolution Time"] = record["Resolution Time"].replace(" ", "T")
    return render_template("edit.html", record=record, id=id)

# Delete Function

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    import pandas as pd

    df = pd.read_csv("phone_data.csv", dtype=str)

    df = df.drop(index=id).reset_index(drop=True)

    df.to_csv("phone_data.csv", index=False)
    flash("Record deleted successfully!", "success")
    return redirect("/view_records")
    
# Generate report
@app.route("/download_records")
@login_required
def download_records():
    file_path = "phone_data.csv"
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name="ip_phone_records.csv"
        )
    else:
        flash("No records found to download.", "danger")
        return redirect("/actions")
# CHART
@app.route("/charts_dashboard")
@login_required
def charts_dashboard():
    import pandas as pd

    try:
        df = pd.read_csv("phone_data.csv")
    except:
        df = pd.DataFrame()

    def get_counts(column):
        if column in df.columns:
            return df[column].value_counts().to_dict()
        return {}

    return render_template(
        "charts_dashboard.html",
        status_data=get_counts("Status"),
        ministry_data=get_counts("Ministry"),
        phone_type_data =get_counts("Phone Type"),
        action_data=get_counts("Action")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
