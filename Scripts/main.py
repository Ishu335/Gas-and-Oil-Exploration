import tkinter as tk
from tkinter import messagebox
import subprocess

# --- Function to validate and run ---
def validate_and_run():
    result_text.delete("1.0", tk.END)
    critical_passed = True
    warning_conditions = []

    for label, var in validation_states.items():
        value = var.get()
        passed = value == 1

        result_text.insert(tk.END, f"{label}: {'Yes ✅' if passed else 'No ❌'}\n")

        if not passed:
            # Allow Temperature and Wave Height to fail with warning
            if label in ["Wave Height (0-3m)", "Temperature (80-120°C)"]:
                warning_conditions.append(label)
            else:
                critical_passed = False  # Critical condition failed

    # --- Decision Logic ---
    if critical_passed:
        if warning_conditions:
            result_text.insert(tk.END, "\n⚠️ Warning: These conditions did NOT meet the criteria:\n")
            for cond in warning_conditions:
                result_text.insert(tk.END, f"   - {cond}\n")
            result_text.insert(tk.END, "\nProceeding with caution...\n")
        else:
            result_text.insert(tk.END, "\n✅ All conditions met. Running the script...\n")

        # Run the external script
        try:
            subprocess.Popen(["python", r"predication.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Script execution failed: {e}")
    else:
        result_text.insert(tk.END, "\n❌ One or more *critical* conditions failed. Script not executed.\n")


# --- GUI Setup ---
root = tk.Tk()
root.title("🛢️ Oil & Gas Condition Validator")
root.geometry("700x750")
root.configure(bg="#f5f9fc")

# --- Styles ---
PRIMARY_COLOR = "#34495e"
ACCENT_COLOR = "#2ecc71"
FONT_HEADER = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_LABEL = ("Segoe UI", 11)
FONT_RESULT = ("Consolas", 10)

# --- Title & Subtitle ---
tk.Label(root, text="🛢️ Oil & Gas Condition Validator", font=FONT_HEADER, bg="#f5f9fc", fg=PRIMARY_COLOR).pack(pady=(30, 10))
tk.Label(root, text="Toggle each condition as Valid (Yes ✅) or Invalid (No ❌)", font=FONT_SUBTITLE, bg="#f5f9fc", fg="#555").pack()

# --- Validation States ---
validation_states = {
    "Sea Level + Water Depth (0-1500m)": tk.IntVar(value=1),
    "Temperature (80-120°C)": tk.IntVar(value=1),
    "Pressure (10-50 MPa)": tk.IntVar(value=1),
    "Seismic Risk (< 4.5 Magnitude)": tk.IntVar(value=1),
    "Wave Height (0-3m)": tk.IntVar(value=1)
}

# --- Condition Toggles ---
for label, var in validation_states.items():
    frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
    frame.pack(fill="x", padx=40, pady=10)

    tk.Label(frame, text=label, font=FONT_LABEL, bg="#ffffff", anchor="w", width=40).pack(side=tk.LEFT, padx=(10, 5), pady=10)
    tk.Radiobutton(frame, text="Yes ✅", variable=var, value=1, bg="#ffffff", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame, text="No ❌", variable=var, value=0, bg="#ffffff", font=("Segoe UI", 10)).pack(side=tk.LEFT)

# --- Button Hover Effects ---
def on_enter(e):
    run_button.config(bg="#28b463")

def on_leave(e):
    run_button.config(bg=ACCENT_COLOR)

# --- Validate & Run Button ---
run_button = tk.Button(root, text="🚀 Validate & Run Script", command=validate_and_run,
                       bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 13, "bold"),
                       relief="flat", padx=20, pady=10, bd=0, cursor="hand2")
run_button.pack(pady=30)
run_button.bind("<Enter>", on_enter)
run_button.bind("<Leave>", on_leave)

# --- Output Result Section ---
tk.Label(root, text="📋 Validation Results", font=("Segoe UI", 13, "bold"), bg="#f5f9fc", fg="#2c3e50").pack()
result_text = tk.Text(root, height=12, width=75, font=FONT_RESULT, bd=1, relief="solid", bg="#ffffff")
result_text.pack(pady=10)

# --- Start App ---
root.mainloop()
