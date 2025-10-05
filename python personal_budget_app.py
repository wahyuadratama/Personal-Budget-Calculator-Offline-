import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import ttkbootstrap
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
    USE_TTKBOOTSTRAP = True
except ImportError:
    USE_TTKBOOTSTRAP = False

DATA_FILE = "budget_data.json"

# ----------------------------
# Data Handling
# ----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def export_csv(data):
    if not data:
        messagebox.showwarning("Warning", "No data to export.")
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    if filepath:
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Type", "Amount", "Description"])
            for item in data:
                writer.writerow([item["date"], item["category"], item["type"], item["amount"], item["description"]])
        messagebox.showinfo("Success", f"Data exported to {filepath}")

# ----------------------------
# Main App
# ----------------------------
class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Personal Budget Calculator")
        self.root.geometry("900x600")
        self.data = load_data()

        # Notebook tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.add_frame = ttk.Frame(self.notebook)
        self.report_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        self.notebook.add(self.add_frame, text="➕ Add Transaction")
        self.notebook.add(self.report_frame, text="📑 Reports")

        # Build UI
        self.build_dashboard()
        self.build_add_transaction()
        self.build_reports()

    # ------------------ Dashboard ------------------
    def build_dashboard(self):
        # Summary
        summary_frame = ttk.LabelFrame(self.dashboard_frame, text="💡 Summary", padding=15)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.income_var = tk.StringVar()
        self.expense_var = tk.StringVar()
        self.balance_var = tk.StringVar()

        ttk.Label(summary_frame, text="Total Income:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(summary_frame, textvariable=self.income_var, style="success.TLabel", font=("Segoe UI", 11)).grid(row=0, column=1, sticky="w")

        ttk.Label(summary_frame, text="Total Expenses:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(summary_frame, textvariable=self.expense_var, style="danger.TLabel", font=("Segoe UI", 11)).grid(row=1, column=1, sticky="w")

        ttk.Label(summary_frame, text="Balance:", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(summary_frame, textvariable=self.balance_var, style="info.TLabel", font=("Segoe UI", 11)).grid(row=2, column=1, sticky="w")

        # Table
        table_frame = ttk.LabelFrame(self.dashboard_frame, text="📋 Transactions", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Date", "Category", "Type", "Amount", "Description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Buttons
        btn_frame = ttk.Frame(self.dashboard_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="🗑 Delete Selected", bootstyle="danger", command=self.delete_transaction).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📤 Export CSV", bootstyle="primary", command=lambda: export_csv(self.data)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📈 Show Charts", bootstyle="success", command=self.show_charts).pack(side="left", padx=5)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_income = sum(float(x["amount"]) for x in self.data if x["type"] == "Income")
        total_expense = sum(float(x["amount"]) for x in self.data if x["type"] == "Expense")
        balance = total_income - total_expense

        self.income_var.set(f"{total_income:.2f}")
        self.expense_var.set(f"{total_expense:.2f}")
        self.balance_var.set(f"{balance:.2f}")

        for item in self.data:
            self.tree.insert("", "end", values=(item["date"], item["category"], item["type"], item["amount"], item["description"]))

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No transaction selected.")
            return
        values = self.tree.item(selected[0], "values")
        self.data = [x for x in self.data if not (
            x["date"] == values[0] and
            x["category"] == values[1] and
            x["type"] == values[2] and
            str(x["amount"]) == values[3] and
            x["description"] == values[4]
        )]
        save_data(self.data)
        self.refresh_dashboard()

    def show_charts(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to show charts.")
            return

        chart_win = tk.Toplevel(self.root)
        chart_win.title("📊 Charts")

        # Expense pie chart
        expenses = {}
        for x in self.data:
            if x["type"] == "Expense":
                expenses[x["category"]] = expenses.get(x["category"], 0) + float(x["amount"])

        if expenses:
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(expenses.values(), labels=expenses.keys(), autopct="%1.1f%%")
            ax1.set_title("Expense Distribution")
            canvas1 = FigureCanvasTkAgg(fig1, master=chart_win)
            canvas1.get_tk_widget().pack(side="left")

        # Income vs Expense bar chart
        months = {}
        for x in self.data:
            month = x["date"][:7]  # YYYY-MM
            if month not in months:
                months[month] = {"Income": 0, "Expense": 0}
            months[month][x["type"]] += float(x["amount"])

        if months:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            labels = list(months.keys())
            income_vals = [months[m]["Income"] for m in labels]
            expense_vals = [months[m]["Expense"] for m in labels]

            ax2.bar(labels, income_vals, label="Income")
            ax2.bar(labels, expense_vals, bottom=income_vals, label="Expense")
            ax2.set_title("Monthly Income vs Expenses")
            ax2.legend()
            canvas2 = FigureCanvasTkAgg(fig2, master=chart_win)
            canvas2.get_tk_widget().pack(side="right")

    # ------------------ Add Transaction ------------------
    def build_add_transaction(self):
        frame = ttk.LabelFrame(self.add_frame, text="➕ Add New Transaction", padding=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.category_entry = ttk.Entry(frame)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Type:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.type_var, values=["Income", "Expense"]).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Amount:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Description:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(frame)
        self.desc_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Add Transaction", bootstyle="success", command=self.add_transaction).grid(row=5, column=0, columnspan=2, pady=10)

    def add_transaction(self):
        date = self.date_entry.get().strip()
        category = self.category_entry.get().strip()
        ttype = self.type_var.get()
        amount = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not date or not category or not ttype or not amount:
            messagebox.showerror("Error", "All fields except description are required.")
            return
        try:
            float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be numeric.")
            return

        self.data.append({
            "date": date,
            "category": category,
            "type": ttype,
            "amount": float(amount),
            "description": desc
        })
        save_data(self.data)
        messagebox.showinfo("Success", "Transaction added.")
        self.refresh_dashboard()
        self.date_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    # ------------------ Reports ------------------
    def build_reports(self):
        frame = ttk.LabelFrame(self.report_frame, text="📑 Reports", padding=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Enter Month (YYYY-MM):").pack(pady=5)
        self.report_month = ttk.Entry(frame)
        self.report_month.pack(pady=5)

        ttk.Button(frame, text="Generate Report", bootstyle="primary", command=self.generate_report).pack(pady=5)

        self.report_text = tk.Text(frame, height=15, bg="#f8f9fa", font=("Consolas", 10))
        self.report_text.pack(fill="both", expand=True, pady=10)

    def generate_report(self):
        month = self.report_month.get().strip()
        if not month:
            messagebox.showerror("Error", "Please enter month in format YYYY-MM.")
            return

        monthly_data = [x for x in self.data if x["date"].startswith(month)]
        if not monthly_data:
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, "No data for this month.")
            return

        income = sum(float(x["amount"]) for x in monthly_data if x["type"] == "Income")
        expense = sum(float(x["amount"]) for x in monthly_data if x["type"] == "Expense")
        balance = income - expense

        report = f"Report for {month}\n"
        report += f"Total Income: {income:.2f}\n"
        report += f"Total Expenses: {expense:.2f}\n"
        report += f"Balance: {balance:.2f}\n\n"
        report += "Transactions:\n"
        for item in monthly_data:
            report += f"{item['date']} - {item['category']} - {item['type']} - {item['amount']} - {item['description']}\n"

        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)

# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    if USE_TTKBOOTSTRAP:
        app = tb.Window(themename="cosmo")  # tema modern
    else:
        app = tk.Tk()
    BudgetApp(app)
    app.mainloop()
