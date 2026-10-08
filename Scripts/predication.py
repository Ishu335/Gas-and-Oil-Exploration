import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

class OilGasPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractable Oil & Gas Predictor")
        self.root.geometry("700x650")

        self.model = None
        self.data = None
        self.static_model = None
        self.static_data = None

        # UI Elements
        tk.Label(root, text="📊 Oil & Gas Prediction System", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Button(root, text="📁 Load CSV File", command=self.load_data, width=30).pack(pady=5)
        tk.Button(root, text="🧠 Train Custom Model", command=self.train_model, width=30).pack(pady=5)
        tk.Button(root, text="🔍 Predict with Custom Model", command=self.predict, width=30).pack(pady=5)
        tk.Button(root, text="📈 Predict with Static Model", command=self.predict_static, width=30).pack(pady=5)
        tk.Button(root, text="📊 Visualize Data", command=self.visualize_data, width=30).pack(pady=5)

        self.range_frame = tk.Frame(root)
        self.range_frame.pack(pady=10)

        self.status = tk.Label(root, text="", fg="green")
        self.status.pack(pady=10)

        # Load static model and data
        try:
            self.static_data = pd.read_csv(r"dataset\Realistic_oil_gas_dataset_final.csv")
            self.static_model = joblib.load(r"train_model\ensemble_model_stacking.joblib")
            self.status.config(text="📦 Static model loaded and ready!")
            self.display_feature_ranges()
        except Exception as e:
            self.status.config(text=f"⚠️ Failed to load static model: {e}")

    def display_feature_ranges(self):
        for widget in self.range_frame.winfo_children():
            widget.destroy()

        tk.Label(self.range_frame, text="📌 Static Feature Ranges", font=("Arial", 12, "bold")).pack()
        range_table = tk.Frame(self.range_frame)
        range_table.pack()

        tk.Label(range_table, text="Feature", font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=30).grid(row=0, column=0)
        tk.Label(range_table, text="Min Value", font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=20).grid(row=0, column=1)
        tk.Label(range_table, text="Max Value", font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=20).grid(row=0, column=2)

        for i, col in enumerate(self.static_data.columns[:-1]):
            min_val = self.static_data[col].min()
            max_val = self.static_data[col].max()
            tk.Label(range_table, text=col, borderwidth=1, relief="solid", width=30).grid(row=i+1, column=0)
            tk.Label(range_table, text=f"{min_val:.2f}", borderwidth=1, relief="solid", width=20).grid(row=i+1, column=1)
            tk.Label(range_table, text=f"{max_val:.2f}", borderwidth=1, relief="solid", width=20).grid(row=i+1, column=2)

    def load_data(self):
        file_path = filedialog.askopenfilename()
        try:
            self.data = pd.read_csv(file_path)
            self.status.config(text="✅ Custom dataset loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def train_model(self):
        if self.data is None:
            messagebox.showwarning("No Data", "Please load a dataset first.")
            return

        try:
            df = self.data.copy()

            # Step 1: Handle missing values
            df = df.dropna() 

            # Step 2: Remove outliers using IQR (Interquartile Range)
            Q1 = df.quantile(0.25)
            Q3 = df.quantile(0.75)
            IQR = Q3 - Q1
            df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]

            # Step 3: Split features and target
            X = df.drop(columns=["Extractable_Oil_Gas"])
            y = df["Extractable_Oil_Gas"]

            # Step 4: Split into training/testing
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Step 5: Create pipeline
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('model', RandomForestRegressor(n_estimators=100, random_state=42))
            ])

            # Step 6: Train model
            pipeline.fit(X_train, y_train)

            # Step 7: Predict and evaluate
            y_pred = pipeline.predict(X_test)
            score = r2_score(y_test, y_pred)

            # Step 8: Save model
            self.model = pipeline
            joblib.dump(self.model, f"custom_model/custom_oil_gas_model.joblib")
            self.status.config(text=f"✅ Custom model trained. R² Score: {score:.4f}")

        except Exception as e:
            messagebox.showerror("Training Error", str(e))


    def predict(self):
        if self.model is None:
            messagebox.showwarning("No Model", "Train the model first.")
            return

        self._open_prediction_window(self.model, self.data.columns[:-1], title="Predict Using Custom Model")

    def predict_static(self):
        if self.static_model is None or self.static_data is None:
            messagebox.showwarning("Model Missing", "Static model not available.")
            return

        self._open_prediction_window(self.static_model, self.static_data.columns[:-1], title="Predict Using Static Model", check_range=True)

    def visualize_data(self):
        try:
                df = self.data if self.data is not None else self.static_data
                source = "Custom Dataset" if self.data is not None else "Static Dataset"
                if df is None:
                    messagebox.showwarning("No Data", "No dataset is available to visualize.")
                    return

                # Calculate correlation matrix
                corr = df.corr()

                # Create a new Tkinter window for visualization
                viz_window = tk.Toplevel(self.root)
                viz_window.title(f"Correlation Heatmap - {source}")
                viz_window.geometry("900x700")

                # Create matplotlib figure
                fig, ax = plt.subplots(figsize=(10, 8))

                # Create heatmap using seaborn
                sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax, cbar=True,
                            square=True, linewidths=0.5, linecolor='gray')

                ax.set_title(f"Feature Correlation Heatmap ({source})", fontsize=14)

                # Embed the plot in Tkinter window
                canvas = FigureCanvasTkAgg(fig, master=viz_window)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))



    def _open_prediction_window(self, model, feature_columns, title, check_range=False):
        input_window = tk.Toplevel(self.root)
        input_window.title(title)

        entries = {}
        for i, col in enumerate(feature_columns):
            tk.Label(input_window, text=col).grid(row=i, column=0, padx=10, pady=5)
            ent = tk.Entry(input_window)
            ent.grid(row=i, column=1, padx=10, pady=5)
            entries[col] = ent

            # Show static range if available
            if check_range and self.static_data is not None:
                min_val = self.static_data[col].min()
                max_val = self.static_data[col].max()
                range_label = f"({min_val:.2f} - {max_val:.2f})"
                tk.Label(input_window, text=range_label, fg="gray").grid(row=i, column=2, padx=5, pady=5)

        def predict_now():
            try:
                values = [float(entries[col].get()) for col in feature_columns]
                df_input = pd.DataFrame([values], columns=feature_columns)

                if check_range:
                    for col in feature_columns:
                        val = df_input[col][0]
                        min_val = self.static_data[col].min()
                        max_val = self.static_data[col].max()
                        if not (min_val <= val <= max_val):
                            messagebox.showwarning(
                                "Value Out of Range",
                                f"{col} = {val} is outside static model range [{min_val:.2f}, {max_val:.2f}].\nPlease train a custom model."
                            )
                            return

                prediction = model.predict(df_input)[0]
                messagebox.showinfo("Prediction", f"🔮 Predicted Extractable Oil & Gas: {prediction:,.2f} Barrel of Oil Equivalent (BOE)")

            except Exception as e:
                messagebox.showerror("Prediction Error", str(e))

        tk.Button(input_window, text="🔮 Predict", command=predict_now).grid(row=len(feature_columns), columnspan=3, pady=10)

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = OilGasPredictorApp(root)
    root.mainloop()
