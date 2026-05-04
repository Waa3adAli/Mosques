import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import difflib
import folium
import webbrowser
import os
import csv


class MosqueDB:
    """Database handler for mosque records."""

    def __init__(self, db_name="mosques.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Mosq(
                ID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                Type TEXT,
                Address TEXT,
                Coordinates TEXT,
                Imam_name TEXT
            )
        """)
        self.conn.commit()

    def display_all(self):
        self.cur.execute("SELECT * FROM Mosq ORDER BY Name")
        return self.cur.fetchall()

    def insert(self, ID, name, mtype, address, coordinates, imam_name):
        self.cur.execute("""
            INSERT INTO Mosq (ID, Name, Type, Address, Coordinates, Imam_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ID, name, mtype, address, coordinates, imam_name))
        self.conn.commit()

    def delete(self, ID):
        self.cur.execute("DELETE FROM Mosq WHERE ID = ?", (ID,))
        self.conn.commit()

    def update_imam(self, ID, new_imam_name):
        self.cur.execute("UPDATE Mosq SET Imam_name = ? WHERE ID = ?", (new_imam_name, ID))
        self.conn.commit()

    def search_by_id(self, ID):
        self.cur.execute("SELECT * FROM Mosq WHERE ID = ?", (ID,))
        return self.cur.fetchone()

    def search_by_name(self, name):
        self.cur.execute("SELECT * FROM Mosq WHERE LOWER(Name) LIKE LOWER(?)", (f"%{name}%",))
        return self.cur.fetchall()

    def get_all_names(self):
        self.cur.execute("SELECT Name FROM Mosq")
        return [row[0] for row in self.cur.fetchall()]

    def export_csv(self, output_file="mosques_export.csv"):
        rows = self.display_all()
        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Type", "Address", "Coordinates", "Imam_name"])
            writer.writerows(rows)

    def close(self):
        self.conn.close()


class MosqueApp:
    """GUI application for managing mosque records."""

    def __init__(self, root):
        self.root = root
        self.root.title("Mosques Management System - Upgraded")
        self.root.geometry("950x560")
        self.db = MosqueDB()

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_type = tk.StringVar(value="Masjid")
        self.var_address = tk.StringVar()
        self.var_coordinates = tk.StringVar()
        self.var_imam = tk.StringVar()

        self.build_ui()
        self.display_all()

    def build_ui(self):
        input_frame = ttk.LabelFrame(self.root, text="Mosque Information")
        input_frame.pack(fill="x", padx=10, pady=10)

        fields = [
            ("ID", self.var_id),
            ("Name", self.var_name),
            ("Address", self.var_address),
            ("Coordinates", self.var_coordinates),
            ("Imam Name", self.var_imam),
        ]

        ttk.Label(input_frame, text="Type").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Combobox(input_frame, textvariable=self.var_type, values=["Masjid", "Jame'a", "Musalla", "Other"], width=14)\
            .grid(row=0, column=5, padx=5, pady=5)

        positions = [(0, 0), (0, 2), (1, 0), (1, 2), (1, 4)]
        for (label, var), (row, col) in zip(fields, positions):
            ttk.Label(input_frame, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="w")
            ttk.Entry(input_frame, textvariable=var, width=22).grid(row=row, column=col + 1, padx=5, pady=5)

        table_frame = ttk.LabelFrame(self.root, text="Mosque Records")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Name", "Type", "Address", "Coordinates", "Imam")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=135)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        button_frame = ttk.LabelFrame(self.root, text="Operations")
        button_frame.pack(fill="x", padx=10, pady=10)

        buttons = [
            ("Display All", self.display_all),
            ("Add Entry", self.add_entry),
            ("Search", self.search_record),
            ("Smart Search", self.smart_search),
            ("Update Imam", self.update_imam),
            ("Delete", self.delete_entry),
            ("Show Selected on Map", self.display_selected_on_map),
            ("Show All on Map", self.display_all_on_map),
            ("Export CSV", self.export_csv),
            ("Clear", self.clear_fields),
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(row=i // 5, column=i % 5, padx=5, pady=5, sticky="ew")

    def validate_coordinates(self, coordinates):
        try:
            lat_str, lon_str = coordinates.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError
            return lat, lon
        except Exception:
            raise ValueError("Coordinates must be in this format: 26.32890,43.97455")

    def get_form_data(self):
        try:
            ID = int(self.var_id.get().strip())
        except ValueError:
            raise ValueError("ID must be a number.")

        name = self.var_name.get().strip()
        if not name:
            raise ValueError("Name is required.")

        coordinates = self.var_coordinates.get().strip()
        if coordinates:
            self.validate_coordinates(coordinates)

        return (
            ID,
            name,
            self.var_type.get().strip(),
            self.var_address.get().strip(),
            coordinates,
            self.var_imam.get().strip(),
        )

    def fill_table(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def display_all(self):
        self.fill_table(self.db.display_all())

    def add_entry(self):
        try:
            self.db.insert(*self.get_form_data())
            messagebox.showinfo("Success", "Mosque added successfully.")
            self.display_all()
            self.clear_fields()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This ID already exists.")
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def search_record(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter a mosque name to search.")
            return
        rows = self.db.search_by_name(name)
        self.fill_table(rows)
        if not rows:
            messagebox.showinfo("Not Found", "No matching mosque found.")

    def smart_search(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter a mosque name to search.")
            return

        exact_rows = self.db.search_by_name(name)
        if exact_rows:
            self.fill_table(exact_rows)
            return

        close_names = difflib.get_close_matches(name, self.db.get_all_names(), n=5, cutoff=0.4)
        rows = []
        for mosque_name in close_names:
            rows.extend(self.db.search_by_name(mosque_name))

        self.fill_table(rows)
        if not rows:
            messagebox.showinfo("No Matches", "No similar mosque names found.")

    def update_imam(self):
        try:
            ID = int(self.var_id.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid ID.")
            return

        new_imam = self.var_imam.get().strip()
        if not new_imam:
            messagebox.showerror("Error", "Enter the new imam name.")
            return

        if not self.db.search_by_id(ID):
            messagebox.showerror("Error", "No mosque found with this ID.")
            return

        self.db.update_imam(ID, new_imam)
        messagebox.showinfo("Success", "Imam name updated successfully.")
        self.display_all()

    def delete_entry(self):
        try:
            ID = int(self.var_id.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid ID.")
            return

        if not self.db.search_by_id(ID):
            messagebox.showerror("Error", "No mosque found with this ID.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            self.db.delete(ID)
            messagebox.showinfo("Success", "Record deleted.")
            self.display_all()
            self.clear_fields()

    def create_map(self, rows, output_file):
        valid_locations = []
        for row in rows:
            try:
                lat, lon = self.validate_coordinates(row[4])
                valid_locations.append((row, lat, lon))
            except Exception:
                continue

        if not valid_locations:
            messagebox.showerror("Error", "No valid coordinates available.")
            return

        avg_lat = sum(item[1] for item in valid_locations) / len(valid_locations)
        avg_lon = sum(item[2] for item in valid_locations) / len(valid_locations)

        mosque_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

        for row, lat, lon in valid_locations:
            popup = f"""
            <b>{row[1]}</b><br>
            ID: {row[0]}<br>
            Type: {row[2]}<br>
            Address: {row[3]}<br>
            Imam: {row[5]}
            """
            folium.Marker(
                 [lat, lon],
                 popup=popup,
                 tooltip=row[1],
                    icon=folium.DivIcon(html="<div style='font-size:30px;'>🕌</div>")
             ).add_to(mosque_map)

        mosque_map.save(output_file)
        webbrowser.open("file://" + os.path.abspath(output_file))

    def display_selected_on_map(self):
        try:
            row = self.get_form_data()
            self.create_map([row], "mosque_map.html")
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def display_all_on_map(self):
        self.create_map(self.db.display_all(), "mosques_all_map.html")

    def export_csv(self):
        output_file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="mosques_export.csv"
        )
        if output_file:
            self.db.export_csv(output_file)
            messagebox.showinfo("Success", "Data exported successfully.")

    def clear_fields(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_type.set("Masjid")
        self.var_address.set("")
        self.var_coordinates.set("")
        self.var_imam.set("")

    def on_select_record(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.var_id.set(values[0])
        self.var_name.set(values[1])
        self.var_type.set(values[2])
        self.var_address.set(values[3])
        self.var_coordinates.set(values[4])
        self.var_imam.set(values[5])


if __name__ == "__main__":
    root = tk.Tk()
    app = MosqueApp(root)
    root.mainloop()
