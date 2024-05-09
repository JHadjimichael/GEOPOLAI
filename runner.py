import framework as fk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Label, StringVar, OptionMenu, Button
from tkinter import Canvas
import sys
import random
import json

initial_countries = [
    [
        "Mean",
        50,
        dict(),
        70000,
        2500,
        0.0,
        dict(),
        {"War Materials":250, "Food":250},
        {"WarDep": 0.5, "PeaceDep":0.5, "EconDep":0.5, "ResearchDep":0.5},
        0.05,
        {"Dominance":0.5, "EconomicSuccess":0.5, "Happiness":0.5},
        10000,
        0.6,
        'llm_president'
    ],
    [
        "Athens",
        60,
        {"Sparta": (-50, "hate"), "Thebes": (-10, "dislike"), "Corinth":(0, "ambivalent")},
        40000,
        30000,
        -0.2,
        {"Sparta": "War", "Thebes": "Peace", "Corinth":"Peace"},
        {"War Materials":200, "Food":200},
        {"WarDep": 0.6, "PeaceDep":0.5, "EconDep":1, "ResearchDep":0.1},
        0.015,
        {"Dominance":0.8, "EconomicSuccess":1, "Happiness":0.1},
        100000,
        0.5
    ],
    [
        "Thebes",
        40,
        {"Sparta": (-30, "dislike"), "Athens": (-30, "dislike"), "Corinth":(20, "like")},
        20000,
        15000,
        -0.1,
        {"Sparta": "Peace", "Athens": "Peace", "Corinth":"Peace"},
        {"War Materials":400, "Food":400},
        {"WarDep": 0.5, "PeaceDep":0.5, "EconDep":0.5, "ResearchDep":0.5},
        0.10,
        {"Dominance":0.5, "EconomicSuccess":0.5, "Happiness":0.5},
        70000,
        0.7
    ],
    [
        "Corinth",
        30,
        {"Sparta": (-30, "dislike"), "Athens": (-30, "dislike"), "Thebes": (20, "like")},
        20000,
        15000,
        -0.1,
        {"Sparta": "Peace", "Athens": "Peace",  "Thebes": "Peace"},
        {"War Materials":200, "Food":300},
        {"WarDep": 0.3, "PeaceDep":0.7, "EconDep":0.5, "ResearchDep":0.6},
        0.05,
        {"Dominance":0.5, "EconomicSuccess":0.5, "Happiness":0.5},
        80000,
        0.6
    ],
    [
            str(1),
            random.randint(25,75),
            dict(),
            random.randint(5000, 15000),
            random.randint(2500, 7500),
            0.0,
            dict(),
            {"War Materials":random.randint(125,375), "Food":random.randint(125,375)},
            {"WarDep": random.random(), "PeaceDep":random.random(), "EconDep":random.random(), "ResearchDep":random.random()},
            random.random()//100+0.05,
            {"Dominance":random.random(), "EconomicSuccess":random.random(), "Happiness":random.random()},
            random.randint(60000, 100000),
            random.randrange(50,70)/100,
            'base'
        ]
]

sim_bed = fk.simulation_bed([initial_countries[0]])

print(f"Number of Countries?")
num_countries = int(input())
for i in range(num_countries-1):
    sim_bed.add_country(
        [
            str(i),
            50,
            dict(),
            70000,
            2500,
            0.0,
            dict(),
            {"War Materials":250, "Food":250},
            {"WarDep": 0.5, "PeaceDep":0.5, "EconDep":0.5, "ResearchDep":0.5},
            0.05,
            {"Dominance":0.5, "EconomicSuccess":0.5, "Happiness":0.5},
            10000,
            0.6,
            'base'
        ]
    )


#sim_bed.print_detailed_country_list()
#print(os.listdir())
#sim_bed.process_planning("planning.yaml")
data_over_time = sim_bed.run(5)
#sim_bed.print_graph()
sim_bed.print_detailed_country_list()

num_graphs = 0

def visualize_statistic_over_time(countries, statistic):
    timestamps = [entry['timestamp'] for entry in data_over_time]
    values_list = dict()
    for country in countries:
        values_list[country] = [entry[country][statistic] for entry in data_over_time]

    fig, ax = plt.subplots(1, 1, figsize=(4,4))
    for country in countries:
        #label=f"{country} - {statistic}"
        ax.plot(timestamps, values_list[country], label=f"{country} - {statistic}")
    ax.set_title(f"{statistic} Over Time")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel(statistic)
    ax.legend()
    ax.grid(True)

    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=3+num_graphs//num_graphs, column=num_graphs)

root = Tk()
root.geometry("700x700")
root.title("Data Visualization")

# Variables to store user selections
selected_country = StringVar()
selected_statistic = StringVar()
selected_data = StringVar()

# Dropdown menu for selecting the country
Label(root, text="Select Country:").grid(row=0, column=0)
countries = [country for entry in data_over_time[0] if entry != 'timestamp' for country in [entry]]
country_dropdown = OptionMenu(root, selected_country, *countries)
country_dropdown.grid(row=1, column=0)


# Dropdown menu for selecting the statistic
Label(root, text="Select Statistic:").grid(row=0, column=1)
statistics = [statistic for entry in data_over_time[0]['Mean'] if entry != 'timestamp' for statistic in [entry]]
statistic_dropdown = OptionMenu(root, selected_statistic, *statistics)
statistic_dropdown.grid(row=1, column=1)

# Button to trigger visualization
def visualize():
    global num_graphs
    num_graphs += 1
    country = selected_country.get()
    statistic = selected_statistic.get()
    visualize_statistic_over_time(countries, statistic)

def clear_graph():
     global num_graphs
     num_graphs = 0

     for widget in root.winfo_children():
        print(type(widget))
        #print(type(Tk.canvas_widget))
        if type(widget) == Canvas:
            #print("deleted!")
            widget.destroy()


def save_data():
    statistics = data_over_time
    json.dump(statistics, open("Data.json", "w"))

Button(root, text="Visualize", command=visualize).grid(row=3, column=0)
Button(root, text="Clear", command=clear_graph).grid(row=3, column=1)
Button(root, text="End Process", command=lambda: sys.exit()).grid(row=3, column=2)
Button(root, text="Save Data", command=save_data).grid(row=1, column=2)

# Run the GUI
root.mainloop()



