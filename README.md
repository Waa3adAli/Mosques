# 🕌 Mosques Management System

A Python desktop application for managing mosque records using a SQLite database, with smart search and interactive map visualization.

## 📌 Project Overview

This project allows users to store, search, update, delete, and visualize mosque information.  
It uses a graphical user interface built with Tkinter, stores records in SQLite, and displays mosque locations on an interactive Folium map.

## ✨ Key Features

- Add new mosque records
- Display all mosque records
- Search mosque by name
- Smart search for similar mosque names
- Update imam name
- Delete mosque records by ID
- Store data in a SQLite database
- Show one selected mosque on a map
- Show all mosque locations on an interactive map
- Export mosque data to CSV

## 🛠️ Technologies Used

- Python
- Jupyter Notebook
- Tkinter
- SQLite
- Folium
- HTML
- CSV

## 📂 Project Files

| File | Description |
|---|---|
| `mosques_upgraded.ipynb` | Improved notebook with explanation and upgraded code |
| `mosques_app.py` | Clean Python version of the upgraded application |
| `mosques.db` | SQLite database containing mosque records |
| `mosque_map.html` | Original generated map |
| `mosques_all_map.html` | Upgraded map showing all mosque locations |
| `requirements.txt` | Libraries needed to run the project |
| `mosques_export.csv` | Exported mosque data |

## 🗃️ Database Structure

Table name: `Mosq`

| Column | Type | Description |
|---|---|---|
| `ID` | INTEGER | Unique mosque ID |
| `Name` | TEXT | Mosque name |
| `Type` | TEXT | Mosque type |
| `Address` | TEXT | Mosque address |
| `Coordinates` | TEXT | Latitude and longitude |
| `Imam_name` | TEXT | Imam name |

## ▶️ How to Run

### Option 1: Run with Jupyter Notebook

1. Open Anaconda Prompt
2. Go to the project folder
3. Run:

```bash
jupyter notebook
```

4. Open:

```text
mosques_upgraded.ipynb
```

5. Run the cells.

### Option 2: Run as a Python app

```bash
python mosques_app.py
```

## 🌍 Map Visualization

To view the interactive map, open:

```text
mosques_all_map.html
```

The map displays all mosque records that have valid coordinates.

## 📦 Install Requirements

```bash
pip install -r requirements.txt
```

## 🚀 Future Improvements

- Add login system
- Add edit screen for all fields
- Add search by location
- Add more mosque records
- Improve the interface design
- Convert the project into a web application

## 👩‍💻 Author

Waad Al-Duraibi
