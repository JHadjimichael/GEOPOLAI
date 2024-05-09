import PIL
import numpy as np
from matplotlib import pyplot as plt
import imageio.v2 as imageio

class province:
    def __init__(self, row, column, terrain, ownership, population):
        self.row = row
        self.column = column
        self.terrain = terrain
        self.ownership = ownership
        self.population = population


#def polit_converter(input):


class map_processor:
    def __init__(self, size, land_map, political_map, population_map):
        self.master_map = np.ndarray((size, size), dtype=province)
        self.size = size
        self.land_data = self.convert_to_numpy(land_map)
        self.political_data = self.convert_to_numpy(political_map)
        self.population_data = self.convert_to_numpy(population_map)

        #print(self.land_data)

        # for row in range(size):
        #     for column in range(size):
        #         land = land_converter(self.land_data[row][column])
        #         polit = self.political_data[row][column]
        #         pop = pop_converter(self.population_data[row][column])
        #         self.master_map[row][column] = province(row, column, land, polit, pop)

    def convert_to_numpy(self, map):
        return imageio.imread(map)
    
    def land_converter(self, input):
        input = (input[0], input[1], input[2])
        if input == (58, 95, 205):
            return 0
        elif input == (255, 255, 255):
            return 1
        else:
            return 999

    def pop_converter(self, raw_input):
        input = (raw_input[0], raw_input[1], raw_input[2])
        print(input)
        if input == (255, 255, 255):
            return (1, 0.8)
        elif input == (51, 51, 51):
            return (2, 0.6)
        elif input == (102, 102, 102):
            return (3, 0.4)
        elif input == (153, 153, 153):
            return (4, 0.2)
        elif input == (204, 204, 204):
            return (5, 1)
        elif input == (58, 95, 205):
            return (0, 0.1)
        else:
            return (1, 1)


    def display_encoded_data(self, data, type, size):
        new_data = np.ndarray((size, size, 4))
        
        for row in range(len(data)):
            for column in range(len(data[0])):
                if type == "LandData":
                    new_data[row][column] = (0, (*self.land_converter(data[row][column]), 1), 0)
                elif type == "PopulationData":
                    new_data[row][column] = (0, 0, *self.pop_converter(data[row][column]))
                
        self.display(new_data)

    def display(self, data):
        #print(self.master[map])
        plt.imshow(data, interpolation='nearest')
        plt.show()



processor = map_processor(100, "LandMap.png", "PoliticalMap.png", "PopulationMap.png")
processor.display(processor.population_data)
processor.display_encoded_data(processor.population_data, "PopulationData", processor.size)
