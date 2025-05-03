import numpy as np
import random

class Resource:
    def __init__(self, name, is_energy=False, value=0):
        self.name = name
        self.is_energy = is_energy
        self.value = value
    
    def __str__(self):
        return self.name

class CompositeResource(Resource):
    def __init__(self, components, creation_cost=0, value=0):
        # Create name by combining component names
        name = ''.join([component.name for component in components])
        super().__init__(name, False, value)
        self.components = components
        self.creation_cost = creation_cost  # Cost in energy (r1) units
    
    def get_components(self):
        return self.components

class Zone:
    def __init__(self, name):
        self.name = name
        self.resources = {}  # Resource -> quantity
    
    def add_resource(self, resource, quantity):
        if resource in self.resources:
            self.resources[resource] += quantity
        else:
            self.resources[resource] = quantity
    
    def remove_resource(self, resource, quantity):
        if resource not in self.resources or self.resources[resource] < quantity:
            return False
        
        self.resources[resource] -= quantity
        if self.resources[resource] == 0:
            del self.resources[resource]
        return True
    
    def get_resource_quantity(self, resource):
        return self.resources.get(resource, 0)
    
    def get_total_value(self):
        """Calculate the total value of all resources in the zone"""
        total = 0
        for resource, quantity in self.resources.items():
            total += resource.value * quantity
        return total
    
    def __str__(self):
        return self.name

class ResourceSystem:
    def __init__(self, num_zones=3):
        # Initialize resource definitions based on T1 table
        self.init_resources_from_table()
        
        # Create zones
        self.zones = [Zone(f'z{i+1}') for i in range(num_zones)]
        
        # Initialize with random resource distribution (only basic resources)
        self.assign_basic_resources_to_zones()
    
    def init_resources_from_table(self):
        """Initialize resources based on the T1 table in the requirements"""
        # Create primary resources
        self.energy = Resource("r1", True, 10)  # r1 is energy with value 10
        self.r2 = Resource("r2", False, 5)      # r2 with value 5
        self.r3 = Resource("r3", False, 7)      # r3 with value 7
        
        self.primary_resources = [self.energy, self.r2, self.r3]
        
        # Store all resources (will include composites later)
        self.all_resources = self.primary_resources.copy()
        self.composite_resources = []
        
        # Define possible composite resources with their components, costs and values
        self.composite_definitions = [
            # components, creation cost, value
            ([self.energy, self.r2], 1, 20),           # r1r2
            ([self.energy, self.r3], 12, 30),          # r1r3
        ]
        
        # Create initial composite resources
        self.r1r2 = self.create_composite_resource_from_def(self.composite_definitions[0])
        self.r1r3 = self.create_composite_resource_from_def(self.composite_definitions[1])
        
        # Add the higher-level composite (r1r2.r1r3)
        self.composite_definitions.append(
            ([self.r1r2, self.r1r3], 40, 140)  # r1r2.r1r3
        )
        self.r1r2_r1r3 = self.create_composite_resource_from_def(self.composite_definitions[2])
    
    def create_composite_resource_from_def(self, definition):
        """Create a composite resource from a definition tuple"""
        components, cost, value = definition
        composite = CompositeResource(components, cost, value)
        self.composite_resources.append(composite)
        self.all_resources.append(composite)
        return composite
    
    def assign_basic_resources_to_zones(self):
        """Assign random quantities of basic resources to zones"""
        for zone in self.zones:
            for resource in self.primary_resources:
                quantity = random.randint(1, 100)
                zone.add_resource(resource, quantity)
    
    def create_composite_resource(self, zone_index, composite_resource):
        """Try to create a composite resource in a specific zone"""
        zone = self.zones[zone_index]
        
        # Check if we have all the required components
        for component in composite_resource.components:
            if zone.get_resource_quantity(component) < 1:
                print(f"Cannot create {composite_resource.name} in {zone.name}: missing {component.name}")
                return False
        
        # Check if we have enough energy for creation
        if zone.get_resource_quantity(self.energy) < composite_resource.creation_cost:
            print(f"Cannot create {composite_resource.name} in {zone.name}: not enough energy")
            return False
        
        # Consume components
        for component in composite_resource.components:
            zone.remove_resource(component, 1)
        
        # Consume energy
        zone.remove_resource(self.energy, composite_resource.creation_cost)
        
        # Add the new composite resource
        zone.add_resource(composite_resource, 1)
        print(f"Created {composite_resource.name} in {zone.name}")
        return True
    
    def display_resource_distribution(self):
        """Display the distribution of resources across zones"""
        print("\nResource Distribution in Zones:")
        print("Zone".ljust(10), end="")
        
        # Print header with resource names
        for resource in self.all_resources:
            print(f"{resource.name}".ljust(8), end="")
        print("| Value".ljust(10))
        
        # Print resource quantities for each zone
        for zone in self.zones:
            print(f"{zone.name}".ljust(10), end="")
            for resource in self.all_resources:
                quantity = zone.get_resource_quantity(resource)
                print(f"{quantity}".ljust(8), end="")
            print(f"| {zone.get_total_value()}".ljust(10))
    
    def display_resource_info(self):
        """Display information about all resources"""
        print("\nResource Information:")
        print("{:<15} {:<25} {:<20} {:<10}".format("Resource", "Components", "Energy Cost", "Value"))
        print("-" * 70)
        
        # Print primary resources
        for resource in self.primary_resources:
            energy_status = " (Energy)" if resource.is_energy else ""
            print("{:<15} {:<25} {:<20} {:<10}".format(
                f"{resource.name}{energy_status}", 
                "", 
                "0", 
                resource.value
            ))
        
        # Print composite resources
        for composite in self.composite_resources:
            components = [comp.name for comp in composite.components]
            print("{:<15} {:<25} {:<20} {:<10}".format(
                composite.name,
                ", ".join(components),
                composite.creation_cost,
                composite.value
            ))
    
    def optimize_zones(self):
        """Attempt to optimize the value of resources in each zone"""
        print("\nOptimizing zones...")
        
        # For each zone, try to create the most valuable composites first
        for i, zone in enumerate(self.zones):
            # Try to create the highest-value composite (r1r2.r1r3) as much as possible
            while self.create_composite_resource(i, self.r1r2_r1r3):
                pass
            
            # Try to create mid-level composites
            while self.create_composite_resource(i, self.r1r3) or self.create_composite_resource(i, self.r1r2):
                pass

# Run the simulation
if __name__ == "__main__":
    system = ResourceSystem(num_zones=3)
    
    # Display initial resource distribution
    print("Initial state:")
    system.display_resource_distribution()
    
    # Display information about all resources
    system.display_resource_info()
    
    # Try to optimize each zone
    system.optimize_zones()
    
    # Display final resource distribution
    print("\nFinal state after optimization:")
    system.display_resource_distribution()
