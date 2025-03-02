import numpy as np
import random

# Define the number of resources and zones
R = 3
Z = 3

# Define primary resources
resources = [f'r{i+1}' for i in range(R)]

# Define zones
zones = [f'z{i+1}' for i in range(Z)]

# Function to assign resources to zones with random quantities and store in a matrix
def assign_resources_to_zones(resources, zones):
    matrix = np.zeros((len(zones), len(resources)))
    for i in range(len(zones)):
        for j in range(len(resources)):
            matrix[i, j] = random.randint(1, 100)
    return matrix

# Run the simulation
if __name__ == "__main__":
    resource_matrix = assign_resources_to_zones(resources, zones)
    
    # Print the matrix
    print("Resource Matrix (Rows: Zones, Columns: Resources):")
    print("     ", "  ".join(resources))
    for i, row in enumerate(resource_matrix):
        print(f"{zones[i]}  ", "  ".join(map(str, row.astype(int))))
