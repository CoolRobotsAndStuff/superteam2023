import numpy as np
import cv2 as cv
import copy
from data_structures.vectors import Position2D
from utilities import StepCounter

class PointGrid:
    def __init__(self, initial_shape, pixel_per_cm, robot_radius_m):
        self.array_shape = np.array(initial_shape, dtype=int)
        self.offsets = self.array_shape // 2

        self.grid_index_max = self.array_shape - self.offsets

        self.grid_index_min = self.offsets * -1

        self.dtype = np.dtype([('detected_points', np.int8, 1),
                               
                               ('seen_by_lidar', np.bool_, 1),

                               ('seen_by_camera', np.bool_, 1),

                               ('has_fixture', np.bool_, 1),
                               ('fixture', np.unicode_, 1),
                               ])
        
        self.to_boolean_threshold = 10#25
        self.delete_threshold = 1

        
        self.arrays = {
            "detected_points": np.zeros(self.array_shape, np.uint8),
            "occupied": np.zeros(self.array_shape, np.bool_),
            "traversable": np.zeros(self.array_shape, np.bool_),
            "navigation_preference": np.zeros(self.array_shape, np.float32),
            "traversed": np.zeros(self.array_shape, np.bool_)
        }


        self.resolution = pixel_per_cm * 100
        
        self.robot_radius = int(robot_radius_m * self.resolution)
        print("ROBOT RADIOUS:", self.robot_radius)
        self.robot_diameter = int(self.robot_radius * 2 + 1)

        self.robot_diameter_template = np.zeros((self.robot_diameter, self.robot_diameter), dtype=np.uint8)
        self.robot_diameter_template = cv.circle(self.robot_diameter_template, (self.robot_radius, self.robot_radius), self.robot_radius, 255, -1)
        self.robot_diameter_template = self.robot_diameter_template.astype(np.bool_)
        
        self.robot_diameter_indexes = self.__get_circle_template_indexes(self.robot_radius)

        self.preference_template = self.__generate_quadratic_circle_gradient(self.robot_radius, self.robot_radius * 2)

    def coordinates_to_grid_index(self, coordinates):
        if isinstance(coordinates, np.ndarray):
            coords = (coordinates * self.resolution).astype(int)

        return np.array([coords[1], coords[0]])

    def grid_index_to_coordinates(self, grid_index):
        if isinstance(grid_index, np.ndarray):
            index = (grid_index.astype(float) / self.resolution)
        
        return np.array([index[1], index[0]])
        
    def clean_up(self):
        self.arrays["detected_points"] = self.arrays["detected_points"] * (self.arrays["detected_points"] > self.delete_threshold)

    def load_point_cloud(self, point_cloud, robot_position):
        for p in point_cloud:
            p1 = np.array(p)
            p1 += robot_position
            p1 = self.coordinates_to_grid_index(p1)

            self.expand_grid_to_grid_index(p1)
            position = self.grid_index_to_array_index(p1)
            
            if not self.arrays["occupied"][position[0], position[1]]:
                if self.arrays["detected_points"][position[0], position[1]] < self.to_boolean_threshold:
                    self.arrays["detected_points"][position[0], position[1]] += 1
                elif self.arrays["detected_points"][position[0], position[1]] >= self.to_boolean_threshold:
                    self.arrays["occupied"][position[0], position[1]] = True
       
        self.clean_up()
        
        occupied_as_int = self.arrays["occupied"].astype(np.uint8)

        self.arrays["traversable"] = cv.filter2D(occupied_as_int, -1, self.robot_diameter_template.astype(np.uint8))
        self.arrays["traversable"] = self.arrays["traversable"].astype(np.bool_)

        self.arrays["navigation_preference"] = cv.filter2D(occupied_as_int, -1, self.preference_template)

    def load_robot_position(self, robot_position):
        robot_grid_index = self.coordinates_to_grid_index(robot_position)
        circle = self.robot_diameter_indexes + np.array(robot_grid_index)
        for item in circle:
            self.expand_grid_to_grid_index(item)
            array_index = self.grid_index_to_array_index(item)
            self.arrays["traversed"][array_index[0], array_index[1]] = True

    def array_index_to_grid_index(self, array_index: np.ndarray):
        return array_index[0] - self.offsets[0], array_index[1] - self.offsets[1]
    
    def grid_index_to_array_index(self, grid_index: np.ndarray):
        return  grid_index[0] + self.offsets[0], grid_index[1] + self.offsets[1]

    def expand_grid_to_grid_index(self, grid_index: np.ndarray):
        array_index = self.grid_index_to_array_index(grid_index)
        if array_index[0] + 1 > self.array_shape[0]:
            self.add_end_row(array_index[0] - self.array_shape[0] + 1)

        if array_index[1] + 1 > self.array_shape[1]:
            self.add_end_column(array_index[1] - self.array_shape[1] + 1)

        if array_index[0] < 0:
            self.add_begining_row(array_index[0] * -1)
        if array_index[1] < 0:
            self.add_begining_column(array_index[1] * -1)
    
    def add_end_row(self, size):
        self.array_shape = np.array([self.array_shape[0] + size, self.array_shape[1]])
        
        for key in self.arrays:
            self.arrays[key] = self.__add_end_row_to_grid(self.arrays[key], size)
        
    def add_begining_row(self, size):
        self.offsets[0] += size
        self.array_shape = np.array([self.array_shape[0] + size, self.array_shape[1]])

        for key in self.arrays:
            self.arrays[key] = self.__add_begining_row_to_grid(self.arrays[key], size)

    def add_end_column(self, size):
        self.array_shape = np.array([self.array_shape[0], self.array_shape[1] + size])

        for key in self.arrays:
            self.arrays[key] = self.__add_end_column_to_grid(self.arrays[key], size)

    def add_begining_column(self, size):
        self.offsets[1] += size
        self.array_shape = np.array([self.array_shape[0], self.array_shape[1] + size])

        for key in self.arrays:
            self.arrays[key] = self.__add_begining_column_to_grid(self.arrays[key], size)


    def __add_end_row_to_grid(self, grid, size):
        grid = np.vstack((grid, np.zeros((size, self.array_shape[1]), dtype=grid.dtype)))
        return grid
    
    def __add_begining_row_to_grid(self, grid, size):
        grid = np.vstack((np.zeros((size, self.array_shape[1]), dtype=grid.dtype), grid))
        return grid
    
    def __add_end_column_to_grid(self, grid, size):
        grid = np.hstack((grid, np.zeros((self.array_shape[0], size), dtype=grid.dtype)))
        return grid

    def __add_begining_column_to_grid(self, grid, size):
        grid = np.hstack((np.zeros((self.array_shape[0], size), dtype=grid.dtype), grid))
        return grid
    
    def __generate_quadratic_circle_gradient(self, min_radius, max_radius):
        min_radius = round(min_radius)
        max_radius = round(max_radius)
        template = np.zeros((max_radius * 2 + 1, max_radius * 2 + 1), dtype=np.float32)
        for i in range(max_radius, min_radius, -1):
            print("i:", i)
            template = cv.circle(template, (max_radius, max_radius), i, max_radius ** 2 - i ** 2, -1)
        
        return template * 0.1
    
    def __generate_linear_circle_gradient(self, min_radius, max_radius):
        min_radius = round(min_radius)
        max_radius = round(max_radius)
        template = np.zeros((max_radius * 2 + 1, max_radius * 2 + 1), dtype=np.float32)
        for i in range(max_radius, min_radius, -1):
            print("i:", i)
            template = cv.circle(template, (max_radius, max_radius), i, max_radius - i, -1)
        
        return template * 0.5
    
    def __get_circle_template_indexes(self, radius):
        diameter = int(radius * 2 + 1)

        diameter_template = np.zeros((diameter, diameter), dtype=np.uint8)
        diameter_template = cv.circle(diameter_template, (radius, radius), radius, 255, -1)
        diameter_template = self.robot_diameter_template.astype(np.bool_)

        diameter_indexes = []
        for x, row in enumerate(diameter_template):
            for y, val in enumerate(row):
                if val:
                    diameter_indexes.append((x - radius, y - radius))
        
        return np.array(diameter_indexes) 

    
    def get_colored_grid(self):
        color_grid = np.zeros((self.array_shape[0], self.array_shape[1], 3), dtype=np.float32)

        color_grid[self.arrays["traversed"]] = (.5, 0., .5)
        color_grid[:, :, 1] = self.arrays["navigation_preference"][:, :] / 100
        color_grid[self.arrays["traversable"]] = (255, 0, 0)
        color_grid[self.arrays["occupied"]] = (255, 255, 255)
        

        
        return color_grid
    
    def print_grid(self):
        cv.imshow("circle_template", self.preference_template / 4)
        #cv.imshow("test", self.get_colored_grid())