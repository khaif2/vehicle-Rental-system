from abc import ABC, abstractmethod
from collections import deque

# ------------------- Vehicle and User Classes -------------------

class Rentable(ABC):
    @abstractmethod
    def calculate_rental_charge(self, days: int) -> float:
        pass

class Vehicle(Rentable):
    def __init__(self, vehicle_id, brand, model):
        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self.is_available = True

    def calculate_rental_charge(self, days: int) -> float:
        return 0  # Default, overridden by subclasses

    def __str__(self):
        return f"{self.brand} {self.model} (ID: {self.vehicle_id})"

class Car(Vehicle):
    def __init__(self, vehicle_id, brand, model, seats):
        super().__init__(vehicle_id, brand, model)
        self.seats = seats

    def calculate_rental_charge(self, days: int) -> float:
        return 1500 * days

class Bike(Vehicle):
    def calculate_rental_charge(self, days: int) -> float:
        return 600 * days

class Truck(Vehicle):
    def calculate_rental_charge(self, days: int) -> float:
        return 4000 * days

class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __str__(self):
        return f"{self.name} (ID: {self.user_id})"


# ------------------- Rental and RentalSystem Classes -------------------

class Rental:
    def __init__(self, user, vehicle, days):
        self.user = user
        self.vehicle = vehicle
        self.days = days
        self.total_charge = vehicle.calculate_rental_charge(days)

    def __str__(self):
        return (f"Rental: {self.vehicle} rented by {self.user} "
                f"for {self.days} days, Total Charge: ₹{self.total_charge}")

class RentalSystem:
    def __init__(self):
        self.inventory = []  # List of all vehicles
        self.user_bookings = {}  # Maps User to list of Rentals
        self.pending_service = deque()  # Queue of vehicles pending service

    def add_vehicle(self, vehicle):
        self.inventory.append(vehicle)
        print(f"Added vehicle: {vehicle}")

    def book_vehicle(self, user, vehicle_id, days):
        vehicle = next((v for v in self.inventory if v.vehicle_id == vehicle_id and v.is_available), None)
        if vehicle:
            vehicle.is_available = False
            rental = Rental(user, vehicle, days)
            if user in self.user_bookings:
                self.user_bookings[user].append(rental)
            else:
                self.user_bookings[user] = [rental]
            print(f"Booking successful: {rental}")
            return rental
        else:
            print(f"Vehicle with ID {vehicle_id} not available.")
            return None

    def return_vehicle(self, vehicle_id):
        vehicle = next((v for v in self.inventory if v.vehicle_id == vehicle_id), None)
        if vehicle and not vehicle.is_available:
            vehicle.is_available = True
            self.pending_service.append(vehicle)
            print(f"Vehicle {vehicle_id} returned and added to service queue.")
        else:
            print(f"Vehicle {vehicle_id} not found or already available.")

    def show_user_rentals(self, user):
        rentals = self.user_bookings.get(user, [])
        if rentals:
            print(f"Rentals for {user}:")
            for rental in rentals:
                print(f"  - {rental}")
        else:
            print(f"No rentals found for {user}.")

    def service_next_vehicle(self):
        if self.pending_service:
            vehicle = self.pending_service.popleft()
            print(f"Servicing vehicle: {vehicle}")
            # Vehicle is already marked available
        else:
            print("No vehicles pending service.")


# ------------------- Admin Class -------------------

class Admin:
    def __init__(self, name, rental_system):
        self.name = name
        self.rental_system = rental_system

    def view_all_vehicles(self):
        print("\nAll Vehicles in Inventory:")
        for vehicle in self.rental_system.inventory:
            status = "Available" if vehicle.is_available else "Rented"
            print(f"  - {vehicle} | Status: {status}")

    def search_vehicles(self, vehicle_type=None, available_only=True):
        results = []
        for vehicle in self.rental_system.inventory:
            if vehicle_type and vehicle.__class__.__name__.lower() != vehicle_type.lower():
                continue
            if available_only and not vehicle.is_available:
                continue
            results.append(vehicle)
        if results:
            print(f"\nSearch Results for type '{vehicle_type}' (Available only: {available_only}):")
            for v in results:
                print(f"  - {v}")
        else:
            print("\nNo vehicles found matching criteria.")

    def remove_vehicle(self, vehicle_id):
        vehicle = next((v for v in self.rental_system.inventory if v.vehicle_id == vehicle_id), None)
        if vehicle:
            if vehicle.is_available:
                self.rental_system.inventory.remove(vehicle)
                print(f"Vehicle {vehicle_id} removed from inventory.")
            else:
                print("Cannot remove vehicle while rented.")
        else:
            print("Vehicle not found.")

    def add_vehicle(self):
        print("\nAdd New Vehicle")
        vtype = input("Enter vehicle type (Car, Bike, Truck): ").strip().capitalize()
        vehicle_id = input("Enter unique vehicle ID (e.g. C008): ").strip()
        brand = input("Enter brand: ").strip()
        model = input("Enter model: ").strip()

        if vtype == "Car":
            try:
                seats = int(input("Enter number of seats: "))
            except ValueError:
                print("Invalid seats number. Aborting.")
                return
            vehicle = Car(vehicle_id, brand, model, seats)
        elif vtype == "Bike":
            vehicle = Bike(vehicle_id, brand, model)
        elif vtype == "Truck":
            vehicle = Truck(vehicle_id, brand, model)
        else:
            print("Unknown vehicle type.")
            return

        # Check if vehicle_id is unique
        exists = any(v.vehicle_id == vehicle_id for v in self.rental_system.inventory)
        if exists:
            print("Vehicle ID already exists! Use a unique ID.")
            return

        self.rental_system.add_vehicle(vehicle)
        print(f"{vtype} added successfully!")


# ------------------- User Registration Function -------------------

def register_user(users):
    print("\n--- User Registration ---")
    name = input("Enter your name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return None

    # Generate new user ID
    existing_ids = [int(uid[1:]) for uid in users.keys() if uid.startswith('U')]
    new_id_num = max(existing_ids) + 1 if existing_ids else 1
    new_user_id = f"U{new_id_num:03d}"

    new_user = User(new_user_id, name)
    users[new_user_id] = new_user
    print(f"User registered successfully! Your User ID is {new_user_id}")
    return new_user


# ------------------- Menu Functions -------------------

def user_menu(user, rental_system):
    while True:
        print(f"\n--- User Menu ({user.name}) ---")
        print("1. View Available Vehicles")
        print("2. Book Vehicle")
        print("3. Return Vehicle")
        print("4. View My Rentals")
        print("5. Logout")

        choice = input("Select option: ")

        if choice == "1":
            admin = Admin("", rental_system)
            admin.search_vehicles(available_only=True)
        elif choice == "2":
            vehicle_id = input("Enter Vehicle ID to book: ").strip()
            try:
                days = int(input("Enter number of days: "))
            except ValueError:
                print("Invalid number of days.")
                continue
            rental_system.book_vehicle(user, vehicle_id, days)
        elif choice == "3":
            vehicle_id = input("Enter Vehicle ID to return: ").strip()
            rental_system.return_vehicle(vehicle_id)
        elif choice == "4":
            rental_system.show_user_rentals(user)
        elif choice == "5":
            print(f"Logging out {user.name}...")
            break
        else:
            print("Invalid choice.")


def admin_menu(admin):
    while True:
        print(f"\n--- Admin Menu ({admin.name}) ---")
        print("1. View All Vehicles")
        print("2. Search Vehicles")
        print("3. Remove Vehicle")
        print("4. Service Next Vehicle")
        print("5. Add New Vehicle")
        print("6. Logout")

        choice = input("Select option: ")

        if choice == "1":
            admin.view_all_vehicles()
        elif choice == "2":
            vehicle_type = input("Enter vehicle type (Car, Bike, Truck) or leave blank: ").strip()
            available_only_str = input("Show only available? (yes/no): ").strip().lower()
            available_only = available_only_str == "yes"
            admin.search_vehicles(vehicle_type=vehicle_type if vehicle_type else None, available_only=available_only)
        elif choice == "3":
            vehicle_id = input("Enter Vehicle ID to remove: ").strip()
            admin.remove_vehicle(vehicle_id)
        elif choice == "4":
            admin.service_next_vehicle()
        elif choice == "5":
            admin.add_vehicle()
        elif choice == "6":
            print("Logging out admin...")
            break
        else:
            print("Invalid choice.")


def main_menu():
    rental_system = RentalSystem()

    vehicles_to_add = [
        Car("C001", "Toyota", "Camry", 5),
        Car("C002", "Honda", "Accord", 5),
        Car("C003", "Ford", "Mustang", 4),
        Car("C004", "BMW", "X5", 5),
        Car("C005", "Audi", "A4", 5),

        Bike("B001", "Honda", "CBR"),
        Bike("B002", "Yamaha", "R15"),
        Bike("B003", "Kawasaki", "Ninja"),
        Bike("B004", "Ducati", "Panigale"),
        Bike("B005", "Suzuki", "GSX-R"),

        Truck("T001", "Volvo", "FH"),
        Truck("T002", "Scania", "R-series"),
        Truck("T003", "Mercedes", "Actros"),
        Truck("T004", "MAN", "TGX"),
        Truck("T005", "Isuzu", "F-Series"),

        Car("C006", "Hyundai", "Elantra", 5),
        Bike("B006", "KTM", "Duke"),
        Truck("T006", "Peterbilt", "379"),
        Car("C007", "Tesla", "Model 3", 5),
        Bike("B007", "Harley-Davidson", "Street 750"),
    ]

    for vehicle in vehicles_to_add:
        rental_system.add_vehicle(vehicle)

    users = {
        "U001": User("U001", "Alice"),
        "U002": User("U002", "Bob"),
    }

    admin = Admin("Manager", rental_system)

    while True:
        print("\n--- Vehicle Rental System ---")
        print("1. User Login")
        print("2. User Registration")  # New option
        print("3. Admin Login")
        print("4. Exit")

        choice = input("Select option: ")

        if choice == "1":
            user_id = input("Enter User ID: ").strip()
            user = users.get(user_id)
            if not user:
                print("User not found.")
                continue
            user_menu(user, rental_system)

        elif choice == "2":
            new_user = register_user(users)
            if new_user:
                user_menu(new_user, rental_system)

        elif choice == "3":
            print("Admin logged in.")
            admin_menu(admin)

        elif choice == "4":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main_menu()
