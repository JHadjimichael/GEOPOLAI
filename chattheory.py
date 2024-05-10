import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import framework as fk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from pprint import pp

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
        'base'
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
print(f"Statistic to track?")
istatistic = input()

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


data_over_time = sim_bed.run(100)
pp(data_over_time[0])

# pp(data_over_time)
countries = [country for entry in data_over_time[0] if entry != 'timestamp' for country in [entry]]


# Define parameters
num_lines = num_countries
update_interval = 100  # in milliseconds
x = np.linspace(0, 100, 100)
line_colors = ['r', 'g', 'b', 'y']
line_styles = ['-', '--', '-.', ':']

# Initialize the figure and axis
fig, ax = plt.subplots()
lines = [ax.plot(x, np.zeros_like(x), linestyle=line_styles[i % len(line_styles)], color=line_colors[i % len(line_colors)], label=f'Variable {i}')[0] for i in range(num_lines)]
ax.legend()

# Update function that will be called for each frame of the animation

past_data = dict()

for country in countries:
    past_data[country] =[]


def update(frame):
    l = []
    for i, line in enumerate(lines):
        y = data_over_time[frame][countries[i]][istatistic]
        l.append(y)
        past_data[countries[i]].append(y)
        line.set_ydata(past_data[countries[i]])
    plt.ylim(0, max(l))
    return lines


# Create the animation
ani = FuncAnimation(fig, update, frames=range(100), interval=update_interval)

# Show the plot
plt.show()