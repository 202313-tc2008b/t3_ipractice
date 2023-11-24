# Iterate through the matrix and print the type of each element
def read_matrix(matrix):
    for y, row in enumerate(matrix):
        for x, element in enumerate(row):
            position = f'{(x,y)}'
            if element == '-':
                road_positions.append(position)
            elif element == 'G':
                green_positions.append(position)
            elif element == 'R':
                red_positions.append(position)
            elif element == '%':
                building_positions.append(position)
            elif element == 'B':
                roundAbout_positions.append(position)
            elif element.isdigit():
                # print('Parking Lot ' + element)
                parkingSpots_positions.append(position)
            elif element == 'W':
                pass
                #print("Disallow going E")
            elif element == 'E':
                pass
                #print("Disallow going W")
            elif element == 'N':
                pass
                #print("Disallow going S")
            elif element == 'S':
                pass
                #print("Disallow going N")
            elif element == 'x':
                pass
                #print("Allow all ")
            else:
                print(f'Unknown Element: {element}')
# Read the file content
with open('layout.txt', 'r') as file:
    nmatL = []
    matrixL = [line.strip().split(',') for line in file.readlines()]
    for row in matrixL[::-1]:
        nmatL.append(row)
        print(row)
""" for r in matrixL:
    print(r) """
with open('flow.txt', 'r') as file:
    matrixF = [line.strip().split(',') for line in file.readlines()]


road_positions = []
building_positions = []
parkingSpots_positions = []
roundAbout_positions = []
green_positions = []
red_positions = []
car = [(0,0)]


read_matrix(matrixL)
read_matrix(matrixF)



    