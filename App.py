import sys

# Custom exceptions for error handling
class InvalidNameError(Exception):
    pass

class InvalidProductError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass

class InvalidPrescriptionError(Exception):
    pass

# Customer class
class Customer:
    def __init__(self, ID, name, reward):
        """Initializes a new customer with an ID, name, and reward points."""
        self.ID = ID
        self.name = name
        self.reward = reward

    def get_id(self):
        """Returns the customer's ID."""
        return self.ID
    
    def get_name(self):
        """Returns the customer's name."""
        return self.name
    
    def get_reward(self):
        pass
    
    def get_discount(self, total_cost):
        pass
    
    def update_reward(self, value):
        pass
    
    def display_info(self):
        pass

# Basic Customer class subtype of customer
class BasicCustomer(Customer):
    reward_rate = 1.0  # Default flat reward rate (100%)

    def __init__(self, ID, name, reward=0):
        """Initializes a basic customer with default reward points."""
        super().__init__(ID, name, reward) 
    
    def get_reward(self, total_cost):
        """Calculates and returns the reward points based on total cost."""
        return round(total_cost * self.reward_rate)
    
    def update_reward(self, value):
        """Updates the reward points for the customer."""
        self.reward += value
    
    def display_info(self):
        """Displays the basic customer's information."""
        print(f"{self.ID}\t {self.name}\t {self.reward_rate:.0%}\t ---\t {self.reward}".expandtabs(14))
    
    @classmethod
    def set_reward_rate(cls, new_rate):
        """Sets a new reward rate for all basic customers."""
        cls.reward_rate = new_rate

# VIP Customer class subtype of customer
class VIPCustomer(Customer):
    reward_rate=1.0

    def __init__(self, ID, name, reward = 0, discount_rate=0.08):
        """Initializes a VIP customer with a discount rate and reward points."""
        super().__init__(ID, name, reward) 
        self.discount_rate = discount_rate
    
    def get_discount(self, total_cost):
        """Calculates and returns the discount based on total cost."""
        return total_cost * self.discount_rate
    
    def get_reward(self, total_cost):
        """Calculates and returns the reward points based on total cost."""
        return round(total_cost * self.reward_rate)
    
    def update_reward(self, value):
        """Updates the reward points for the VIP customer."""
        self.reward += value
    
    def display_info(self):
        """Displays the VIP customer's information."""
        print(f"{self.ID}\t {self.name}\t {self.reward_rate:.0%}\t {self.discount_rate:.0%}\t {self.reward}".expandtabs(14))
    
    @classmethod
    def set_reward_rate(cls, new_rate):
        """Sets a new reward rate for all VIP customers."""
        cls.reward_rate = new_rate
    
    def set_discount_rate(self, new_rate):
        """Sets a new discount rate for the VIP customer."""
        self.discount_rate = new_rate
        
# Product class
class Product:
    def __init__(self, ID, name, price, prescription):
        """Initializes a new product with an ID, name, and price."""
        self.ID = ID
        self.name = name
        self.price = price
        self.prescription = prescription
    
    def get_id(self):
        """Returns the product's ID."""
        return self.ID

    def get_name(self):
        """Returns the product's name."""
        return self.name

    def get_price(self):
        """Returns the product's price."""
        return self.price
    
    def requires_prescription(self):
        """Returns whether the product requires a prescription."""
        return self.prescription

    def display_info(self):
        """Displays the product's information."""
        print(f"{self.ID}\t {self.name}\t {self.price:.2f}\t {'YES' if self.prescription == 'y' else 'NO'}\t --".expandtabs(14))

class Bundle(Product):
    def __init__(self, ID, name, products):
        """Initializes a bundle with an ID, name, and a list of component products and call super class."""
        self.ID = ID
        self.name = name
        self.products = products
        self.price = 0.8 * sum(product.get_price() for product in products)
        self.prescription = any(product.requires_prescription() == 'y' for product in products)
        super().__init__(ID, name, self.price, 'y' if self.prescription else 'n' )

    def display_info(self):
        """Displays the bundle's information."""
        component_ids = ', '.join(product.get_id() for product in self.products)
        presc_str = 'YES' if self.prescription == 'y' else 'NO'
        print(f"{self.ID}\t {self.name}\t {self.price:.2f}\t {presc_str}\t {component_ids}".expandtabs(14))

# Order Class
class Order:
    def __init__(self, customer, product:Product, quantity):
        """Initializes a new order with a customer, product, and quantity."""
        self.customer = customer
        self.product = product
        self.quantity = quantity
    
    def compute_cost(self):
        """Computes and returns the original cost, discount, final cost, and reward points for the order."""
        original_cost = self.product.get_price() * self.quantity
        discount = 0.0  # Initialize discount for non-VIP customers
        final_cost = original_cost
        reward_points = 0

        if isinstance(self.customer, VIPCustomer):
            discount = self.customer.get_discount(original_cost)
            final_cost = original_cost - discount
            reward_points = self.customer.get_reward(final_cost)
        else:
            reward_points = self.customer.get_reward(original_cost)

        return original_cost, discount, final_cost, reward_points

# Records class
class Records:
    def __init__(self):
        """Initializes the Records class with empty customer and product lists."""
        self.customers = []
        self.products = []
    
    def read_customers(self, filename):
        """Reads customer data from a file and stores them in the customer list."""
        try:
            with open(filename, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    if len(data) == 5:
                        customer_id, name, reward_rate, discount_rate, reward = data
                        customer = VIPCustomer(customer_id, name, int(reward), float(discount_rate))
                        self.customers.append(customer)
                    else:
                        customer_id, name, reward_rate, reward = data
                        customer = BasicCustomer(customer_id, name, int(reward))
                        self.customers.append(customer)
        except FileNotFoundError:
            print("Error: Customer file not found!")
            sys.exit()
    
    def read_products(self, filename):
        """Reads product and bundle data from a file and stores them in the product list."""
        try:
            with open(filename, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    if data[0].startswith('B'):
                        bundle_id = data[0]
                        bundle_name = data[1]
                        component_ids = data[2:]
                        components = [self.find_product(pid) for pid in component_ids]
                        bundle = Bundle(bundle_id, bundle_name, components)
                        self.products.append(bundle)
                    else:
                        product_id, name, price, prescription = data
                        product = Product(product_id, name, float(price), prescription)
                        self.products.append(product)
        except FileNotFoundError:
            print("Error: Product file not found!")
            sys.exit()
    
    def find_customer(self, search_value):
        """Finds and returns a customer by their ID or name."""
        for customer in self.customers:
            if customer.get_id() == search_value or customer.get_name() == search_value:
                return customer
        return None
    
    def find_product(self, search_value):
        """Finds and returns a product by its ID or name."""
        for product in self.products:
            if product.get_id() == search_value or product.get_name() == search_value:
                return product
        return None
    
    def list_customers(self):
        """Lists all existing customers."""
        print("\nExisting Customers:")
        print("Customer ID\t Name\t Reward Rate\t Discount Rate\t Reward".expandtabs(8))
        for customer in self.customers:
            customer.display_info()
    
    def list_products(self):
        """Lists all existing products and Bundles."""
        print("\nExisting Products:")
        print("Product ID\t Product Name\t Price\t Dr Prescription\t Bundle".expandtabs(7))
        for product in self.products:
            product.display_info()
            # print(product.requires_prescription())
    
    def highest_id_number(self):
        """Returns the highest customer ID number."""
        last_customer = self.customers[-1]
        last_customer_id = last_customer.get_id()
        return int(last_customer_id[1:])

# Operations class
class Operations:
    def __init__(self):
        """Initializes the Operations class and reads customer and product data from files."""
        self.records = Records()
        self.records.read_customers("CREDIT_DI/customers.txt")
        self.records.read_products("CREDIT_DI/products.txt")

    def display_menu(self):
        """Displays the program menu with available options."""
        print("\n"+"#" * 60)
        print("You can choose from the following options:")
        print("1: Make a purchase")
        print("2: Display existing customers")
        print("3: Display existing products")
        print("0: Exit the program")   
        print("#" * 60)

    def validate_customer(self, customer):
        """Validates that the customer name contains only alphabetic characters or ID exists."""
        customer_details = self.records.find_customer(customer)
        if not customer_details:
            if not customer.isalpha():
                raise InvalidNameError("The customer is not valid. Please enter a valid name or ID.")
    
        return customer_details

    def validate_product(self, product_name):
        """Validates that the product exists."""
        product = self.records.find_product(product_name)
        if not product:
            raise InvalidProductError("The product is not valid. Please enter a valid product name or ID.")
        return product
    
    def validate_quantity(self, quantity):
        """Validates that the quantity is a positive integer."""
        if quantity.isalpha() or int(quantity) <= 0:
            raise InvalidQuantityError("The quantity is not valid. Please enter a valid quantity.")
        else:
            return int(quantity)
        
    def validate_prescription(self, prescription):
        """Validates that the prescription input is either 'y' or 'n'."""
        if prescription not in ('y', 'n'):
            raise InvalidPrescriptionError("The answer is not valid. Please enter a valid answer.")
    
    def make_purchase(self):
        """Guides the user through the purchase process and prints a receipt."""

        while True:
            try:
                customer_name = input("Enter the name of the customer or ID:\n")
                customer = self.validate_customer(customer_name)
                break
            except InvalidNameError as e:
                print(e)
                
        while True:
            try:
                product_name = input("Enter the product name or ID:\n")
                product_details = self.validate_product(product_name)
                break
            except InvalidProductError as e:
                print(e)
        
        while True:
            try:
                quantity = input("Enter the quantity [enter a positive integer only, e.g. 1, 2, 3, 4]:\n")
                quantity = self.validate_quantity(quantity)
                break
            except InvalidQuantityError as e:
                print(e)


        if product_details.requires_prescription() == 'y':
            while True:
                try:
                    prescription_answer = input("This product requires a doctor'prescription, do you have one?\n").lower()
                    self.validate_prescription(prescription_answer)
                    if prescription_answer == "n":
                        print("Sorry. This product cannot be purchased without a doctor's prescription.")
                        return
                    break
                except InvalidPrescriptionError as e:
                    print(e)

        if not customer:
            # Create a new basic customer if not found
            customer = BasicCustomer(f"B{self.records.highest_id_number() + 1}", customer_name)
            self.records.customers.append(customer)
        else:
            if isinstance(customer, VIPCustomer):
                print(f"\nWelcome Our VIP Customer {customer.get_name()}")
            else:
                print(f"\nWelcome Our Basic Customer {customer.get_name()}")

        # Create an order object
        order = Order(customer, product_details, quantity)

        # Calculate order details
        original_cost, discount, final_cost, reward_points = order.compute_cost()

        # Print receipt
        print("\n"+"-" * 40)
        print("Receipt".center(40))
        print("-" * 40)

        print(f"Name:\t {customer.get_name()}".expandtabs(20))
        print(f"Product:\t {product_details.get_name()}".expandtabs(20))
        print(f"Unit Price:\t {original_cost/quantity:.2f} (AUD)".expandtabs(20))
        print(f"Quantity:\t {quantity}".expandtabs(20))
        print("-" * 40)

        # Print original cost and discount if customer is VIP 
        if isinstance(customer, VIPCustomer):
            print(f"Original cost:\t {original_cost:.2f} (AUD)".expandtabs(20))
            print(f"Discount:\t {discount:.2f} (AUD)".expandtabs(20))
        
        
        print(f"Total cost:\t {final_cost:.2f} (AUD)".expandtabs(20))
        print(f"Earned reward:\t {reward_points}".expandtabs(20))

        # Update customer reward points
        customer.update_reward(reward_points)

    def display_customers(self):
        """Prints a formatted list of all customers with their details."""
        self.records.list_customers()
    
    def display_products(self):
        """Prints a formatted list of all products with their details."""
        self.records.list_products()
    
    def run(self):
        """The main loop of the program, handling user input and menu options."""
       
        # Greet message
        print("Welcome to the RMIT pharmacy!")

        while True:
            self.display_menu()

            choice = input("Choose one option: ")
            if choice == '1':
                self.make_purchase()
            elif choice == '2':
                self.display_customers()
            elif choice == '3':
                self.display_products()
            elif choice == '0':
                print("Exiting program...") # Exit message
                break
            else:
                # Display error if enter incorrect input
                print("Invalid Choice. Please choose correct option.")
            
# Main program
if __name__ == "__main__":
    operations = Operations()
    operations.run()