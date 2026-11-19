# LCdr Marlon E Estropia
# Version 5 - 05282025 (GUI + Dual Figures: Time-Series & Histogram)
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import os
import statistics


def tidParser(in_name):
    date_out = []
    tide_out = []

    with open(in_name, 'r') as f:
        table_str = f.read()

    table = table_str.split('\n')
    in_date = ""
    hh = 0
    mm = 0
    ss = 0

    for line in table:
        line = line.strip()
        if not line:
            continue

        if '/' in line:
            in_date = line
            hh = 0
            mm = 0
            ss = 0
        else:
            try:
                # Assuming data is in cm. Use / 1000 if data is in mm.
                tide = int(line) / 100
                dt_obj = parser.parse(f"{in_date} {hh}:{mm}:{ss}")

                date_out.append(dt_obj)
                tide_out.append(tide)

                if mm < 59:
                    mm += 1
                else:
                    mm = 0
                    hh += 1
            except ValueError:
                continue

    return date_out, tide_out


def generate_plot():
    pred_file = pred_entry.get()
    act_file = act_entry.get()
    plot_title = title_entry.get()

    if not os.path.exists(pred_file):
        messagebox.showerror("File Error", "Predicted tide file not found.")
        return
    if not os.path.exists(act_file):
        messagebox.showerror("File Error", "Actual tide file not found.")
        return
    if not plot_title.strip():
        plot_title = "Predicted vs Actual Tide"

    try:
        datetoPlot_pred, tidetoPlot_pred = tidParser(pred_file)
        datetoPlot_actual, tidetoPlot_actual = tidParser(act_file)

        # ---------------------------------------------------------
        # STATISTICAL ANALYSIS (Correlating Data)
        # ---------------------------------------------------------
        dict_pred = dict(zip(datetoPlot_pred, tidetoPlot_pred))
        dict_actual = dict(zip(datetoPlot_actual, tidetoPlot_actual))

        common_dates = set(dict_pred.keys()).intersection(set(dict_actual.keys()))

        differences = []
        for dt in common_dates:
            diff = dict_actual[dt] - dict_pred[dt]
            differences.append(diff)

        stats_text = ""
        has_stats = len(differences) > 0

        if has_stats:
            mean_diff = statistics.mean(differences)
            std_dev = statistics.stdev(differences) if len(differences) > 1 else 0.0

            stats_text = (f"Correlated Points: {len(differences)}\n"
                          f"Mean Diff (Act-Pred): {mean_diff:.3f} m\n"
                          f"Std. Deviation: {std_dev:.3f} m")
        else:
            messagebox.showwarning("Data Warning",
                                   "No overlapping times found. Statistical analysis cannot be generated.")

        # ---------------------------------------------------------
        # FIGURE 1: TIME SERIES PLOT
        # ---------------------------------------------------------
        fig1 = plt.figure(num="Tide Time Series")
        ax1 = fig1.add_subplot()

        ax1.plot(datetoPlot_pred, tidetoPlot_pred, color='r', label='Predicted')
        ax1.plot(datetoPlot_actual, tidetoPlot_actual, color='b', label='Actual')

        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%y'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax1.tick_params(axis='x', labelrotation=90)

        ax1.set_title(plot_title)
        ax1.set_xlabel("Date (UTC-0)")
        ax1.set_ylabel("Height (m)")

        ax1.legend(loc='lower right')
        ax1.grid()
        fig1.tight_layout()

        # ---------------------------------------------------------
        # FIGURE 2: HISTOGRAM & STATISTICS
        # ---------------------------------------------------------
        if has_stats:
            fig2 = plt.figure(num="Statistical Analysis - Differences")
            ax2 = fig2.add_subplot()

            # Plot the histogram
            ax2.hist(differences, bins=30, color='skyblue', edgecolor='black', alpha=0.7)

            # Plot Mean and Standard Deviation lines
            ax2.axvline(mean_diff, color='red', linestyle='dashed', linewidth=2, label=f'Mean')

            if std_dev > 0:
                ax2.axvline(mean_diff + std_dev, color='green', linestyle='dotted', linewidth=2, label='+1 Std Dev')
                ax2.axvline(mean_diff - std_dev, color='green', linestyle='dotted', linewidth=2, label='-1 Std Dev')

            ax2.set_title(f"Histogram of Tide Differences\n({plot_title})")
            ax2.set_xlabel("Difference in Height (m) [Actual - Predicted]")
            ax2.set_ylabel("Frequency")

            # Add the statistical text box
            props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
            ax2.text(0.02, 0.96, stats_text, transform=ax2.transAxes, fontsize=10,
                     verticalalignment='top', bbox=props)

            ax2.legend(loc='upper right')
            ax2.grid(axis='y', alpha=0.5)
            fig2.tight_layout()

        # Show all generated figures simultaneously
        plt.show()

    except Exception as e:
        messagebox.showerror("Plotting Error", f"An error occurred while generating the plot:\n\n{str(e)}")


def browse_file(entry_widget):
    filepath = filedialog.askopenfilename(
        title="Select Tide File",
        filetypes=[("Hypack Tide Files", "*.tid"), ("All Files", "*.*")]
    )
    if filepath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filepath)


# ==========================================
# GUI SETUP
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hypack Tide Plotter & Analyzer - LCdr M.E. Estropia")
    root.geometry("600x250")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True, fill=tk.BOTH)

    # --- Predicted Tide Row ---
    tk.Label(frame, text="Predicted Tide (.tid):", anchor="w").grid(row=0, column=0, sticky="w", pady=5)
    pred_entry = tk.Entry(frame, width=50)
    pred_entry.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(frame, text="Browse...", command=lambda: browse_file(pred_entry)).grid(row=0, column=2, pady=5)

    # --- Actual Tide Row ---
    tk.Label(frame, text="Actual Tide (.tid):", anchor="w").grid(row=1, column=0, sticky="w", pady=5)
    act_entry = tk.Entry(frame, width=50)
    act_entry.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(frame, text="Browse...", command=lambda: browse_file(act_entry)).grid(row=1, column=2, pady=5)

    # --- Plot Title Row ---
    tk.Label(frame, text="Plot Title:", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
    title_entry = tk.Entry(frame, width=50)
    title_entry.grid(row=2, column=1, padx=10, pady=5)

    # --- Generate Button ---
    plot_btn = tk.Button(frame, text="Generate Plot & Analysis", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                         command=generate_plot)
    plot_btn.grid(row=3, column=0, columnspan=3, pady=20, ipadx=20, ipady=5)

    root.mainloop()