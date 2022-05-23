import math
import cv2
import numpy as np
from tabulate import tabulate


# function which calculates euclidean distance between two points
def euc_dis_calculator(p1, p2):
    return math.sqrt(pow((p1[0] - p2[0]), 2) + pow((p1[1] - p2[1]), 2))


# function to plot the coordinates
def plot_points(registration_table,plot, index,color):
    title = f'Coordinates at time:  t{index}'
    for sub_index, coordinates in registration_table.items():
        plot = cv2.circle(plot, (int(coordinates[0]) * 20, int(coordinates[1]) * 20), 6 ,color, -2)
    return plot,title


# function to Visualize the coordinates at different time frames
# previous time frame- denoted in pink
# current time frame- denoted in yellow
def object_tracker_visualization(list_of_registrations):
    previous_frame = {}
    plot = cv2.copyMakeBorder(np.zeros((300, 300, 3), np.uint8), 20, 20, 20, 20, cv2.BORDER_CONSTANT)
    for index, registration_table in enumerate(list_of_registrations):

        if index == 0:
            plot, title = plot_points(registration_table,plot,index,(255, 0, 255))
            plot = cv2.resize(plot, (500, 500))
            cv2.imshow(title, plot)
            previous_frame = registration_table

        else:
            plot = cv2.copyMakeBorder(np.zeros((300, 300, 3), np.uint8), 20, 20, 20, 20, cv2.BORDER_CONSTANT)
            current_frame = registration_table
            plot1, title = plot_points(previous_frame, plot, index, (255, 0, 255))
            plot1, title = plot_points(registration_table, plot1, index, (0, 255, 255))
            for i in range(len(previous_frame)):
                for j in range(len(current_frame)):
                    if i == 0:
                        color = (0, 0, 255)
                    if i == 1:
                        color = (0, 255, 0)
                    if i == 2:
                        color = (150, 150, 150)

                    cv2.arrowedLine(plot1, (int(previous_frame[i][0]) * 20, int(previous_frame[i][1]) * 20),
                                        (int(current_frame[j][0]) * 20, int(current_frame[j][1]) * 20),
                                        color, 1)
            previous_frame = registration_table
            plot1 = cv2.resize(plot1, (500, 500))
            cv2.imshow(title, plot1)

    cv2.waitKey(0)


# function to print the registration table in tabular format
def registration_table_print(registration_table):
    data =[]
    for index, object in registration_table.items():
        data.append([f'Object {index}  |', f'{index}  | ', object])
    print(tabulate(data, headers=["Object Id |", "ID | ", "Coordinate(x-bar,y-bar)"]))
    print("----------------------------------------------------\n")
    return


# function to define the object tracking algorithm
def object_tracker(frames):

#mainting all the registration tables in a list to display the visualization
    list_of_registrations =[]
# registration table dictionary defined
    registration_table = {}
    l = 0
    while l < len(frames):
        print(f'Registration table at time t{l}\n')

        frame = frames[l]

        if len(registration_table) == 0:
            for index, coordinates in enumerate(frame):
                registration_table[index] = coordinates

        else:
            registration_table_temp = {}
            indices_marked = set()
            for index, coordinates in registration_table.items():
                i = 1

                minimum_dist = euc_dis_calculator(coordinates, frame[0])
                minimum_index = 0

# evaluating the minimum distance
                while i < len(frame):
                    distance = euc_dis_calculator(coordinates, frame[i])
                    if distance < minimum_dist:
                        minimum_dist = distance
                        minimum_index = i

                    i = i + 1
                    # end of while

                indices_marked.add(minimum_index)
                registration_table_temp[index] = frame[minimum_index]

# checking for new objects in the frame
            if len(indices_marked) <= len(frame):
                i = 0
                j = len(registration_table_temp)
                while i < len(frame):
                    if i in indices_marked:
                        i = i + 1
                        continue
                    else:
                        registration_table_temp[j] = frame[i]

                    i = i + 1
                    j = j + 1

                registration_table = registration_table_temp

        list_of_registrations.append(registration_table)
        registration_table_print(registration_table)

        l = l + 1
        # end of while

    return registration_table, list_of_registrations


# main function
def main():

# reading txt file
    recordsIO = open("centroid_location_feature_map.txt", "r")

    time_frames = []
    temp_frame = []
    temp_tuple = ()
    i = 0
    records = recordsIO.readlines()
# fetching the txt file records from the string to form a list of list with different frames and their coordinates
    while i < len(records):
        record = records[i]
        if record[0] == 't':
            if i != 0:
                time_frames.append(temp_frame)
                temp_frame = []
        elif record[0] == 'o':
            temp_tuple = (float(records[i+1]), float(records[i+2]))
            temp_frame.append(temp_tuple)
            temp_tuple = ()
        i = i+1

    time_frames.append(temp_frame)
    recordsIO.close()

    registration_table,list_of_registrations = object_tracker(time_frames)
    object_tracker_visualization(list_of_registrations)

if __name__ == "__main__":
    main()
