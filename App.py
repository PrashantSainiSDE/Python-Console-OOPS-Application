import sys
import datetime
import os

# Custom exceptions for error handling
class InvalidNameError(Exception):
    pass

class InvalidProductError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass

class InvalidPrescriptionError(Exception):
    pass

class InvalidPriceError(Exception):
    pass

class InvalidRateError(Exception):
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
    
    def get_current_reward(self):
        """Returns the customer's reward points."""
        return self.reward

    def get_discount(self, total_cost):
        pass
    
    def update_reward(self, value):
        pass
    
    def display_info(self):
        pass

# Basic Customer class, a subtype of customer
class BasicCustomer(Customer):
    reward_rate = 1.0  # Default flat reward rate (100%)

    def __init__(self, ID, name, reward=0):
        """Initializes a basic customer with default reward points."""
        super().__init__(ID, name, reward) 
    
    def get_reward(self, total_cost):
        """Calculates and returns the reward points based on total cost."""
        return round(total_cost * self.reward_rate)
    
    def get_current_reward(self):
        return super().get_current_reward()

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

# VIP Customer class, a subtype of customer
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
    
    def get_discount_rate(self):
        """Returns the discount rate of VIP customer"""
        return self.discount_rate
    
    def get_current_reward(self):
        return super().get_current_reward()

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
    
    def update_price(self, new_price):
        """Updates the product's price with new price"""
        self.price = new_price
    
    def update_prescription(self, prescription):
        """Updates the doctor's prescription requirements"""
        self.prescription = prescription

    def display_info(self):
        """Displays the product's information."""
        print(f"{self.ID}\t {self.name}\t {self.price:.2f}\t {'YES' if self.prescription == 'y' else 'NO'}\t --".expandtabs(14))

# Bundle class, a subtype of Product
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
    def __init__(self, customer, products, quantities):
        """Initializes a new order with a customer, products, and quantities."""
        self.customer = customer
        self.products = products
        self.quantities = quantities
    
    def compute_cost(self):
        """Computes and returns the original cost, discount, final cost, and reward points for the order."""
        original_cost = sum(product.get_price() * quantity for product, quantity in zip(self.products, self.quantities))
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
    
    def apply_reward_points(self, final_cost):
        """Applies reward points to reduce the final cost if the customer has more than 100 points."""
        if self.customer.reward >= 100:
            reward_deduction = (self.customer.reward // 100) * 10
            final_cost -= reward_deduction
            self.customer.reward %= 100
            if final_cost < 0:
                final_cost = 0
        return final_cost

# OrderHistory class, a subtype of Order
class OrderHistory(Order):
    def __init__(self, customer, products, quantities, total_cost, earned_rewards, date_time):
        """Initializes a new order history with a customer, products, quantities, total cost, earned rewards and date."""
        super().__init__(customer, products, quantities)
        self.total_cost = total_cost
        self.earned_rewards = earned_rewards
        self.date_time = datetime.datetime.strftime(date_time, "%d/%m/%Y %H:%M:%S") if isinstance(date_time, datetime.datetime) else date_time

    def display_info(self):
        """Displays the order history information."""
        products_str = ', '.join(f'{quantity} x {product.get_id()}' for product, quantity in zip(self.products,self.quantities))

        dt = datetime.datetime.strptime(self.date_time, "%d/%m/%Y %H:%M:%S")
        readable_string = dt.strftime("%a, %d/%b/%y at %H:%M")

        print(f"{self.customer.get_name():<7} {products_str:<23} {self.total_cost}\t {self.earned_rewards}\t {readable_string}".expandtabs(8))

    def get_customer_id(self):
        """Returns the customer's id"""
        return self.customer.get_id()
    
    def get_total_cost(self):
        """Returns the total cost of order"""
        return self.total_cost
    
    def get_earned_rewards(self):
        """Returns the earned reward of order"""
        return self.earned_rewards
    
    def get_date_time(self):
        """Returns the date time of order"""
        return self.date_time
    
# Records class
class Records:
    def __init__(self):
        """Initializes the Records class with empty customer, product lists and order history."""
        self.customers = []
        self.products = []
        self.order_history =[]
    
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
                        BasicCustomer.reward_rate = float(reward_rate)
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
    
    def read_orders(self, filename):
        """Reads order history data from a file and stores them in the order history list."""
        try:
            with open(filename, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    customer_id_or_name = data[0]
                    customer = self.find_customer(customer_id_or_name)
                    total_cost = float(data[-3])
                    earned_rewards = int(data[-2])
                    date_time = data[-1]

                    products = []
                    quantities = []
                    for i in range(1, len(data) - 3, 2):
                        product_id_or_name = data[i]
                        quantity = int(data[i+1])
                        product = self.find_product(product_id_or_name)
                        products.append(product)
                        quantities.append(quantity)

                    order_history = OrderHistory(customer,products,quantities, total_cost, earned_rewards, date_time)
                    self.order_history.append(order_history)
                    customer.update_reward(earned_rewards)

        except FileNotFoundError:
            print("Cannot load the order file.\n")

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
    
    def find_orders(self, customer):
        """Find and return the order history of a given customer"""
        return [history for history in self.order_history if customer.get_id() == history.get_customer_id() ]

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
    
    def list_orders(self):
        """Lists all completed order's history"""
        print("\nOrder history of all customers:")
        print(f"Name\t {'Products':<19} {'Total Cost':<10} Rewards\t Order Time".expandtabs(7))
        for order in self.order_history:
            order.display_info()

    def highest_id_number(self):
        """Returns the highest customer ID number."""
        last_customer = self.customers[-1]
        last_customer_id = last_customer.get_id()
        return int(last_customer_id[1:])

    def add_or_update_product(self, name, price, prescription):
        """Adds a new product or updates an existing product's price and prescription requirement."""
        product:Product = self.find_product(name)
        if product:
            product.update_price(price)
            product.update_prescription(prescription)
        else:
            new_id = f"P{len(self.products) + 1}"
            new_product = Product(new_id, name, price, prescription)
            self.products.append(new_product) 

    def save_customers(self, filename):
        """Write the details of current existing customers in the file"""
        with open(filename, 'w') as file:
            for customer in self.customers:
                file.write(f"{customer.get_id()}, {customer.get_name()}, {customer.reward_rate}, {f'{customer.get_discount_rate()}, ' if isinstance(customer, VIPCustomer) else ''}{customer.get_current_reward()}\n")

    def save_products(self, filename):
        """Write the details of current existing products in the file"""
        with open(filename, 'w') as file:
            for product in self.products:
                if product.get_id().startswith('B'):
                    file.write(f"{product.get_id()}, {product.get_name()}, {', '.join(product.get_id() for product in product.products)}\n")
                    
                else:
                    file.write(f"{product.get_id()}, {product.get_name()}, {product.get_price()}, {product.requires_prescription()}\n")

    def save_orders(self, filename):
        """Write the details of completed orders in the file"""
        with open(filename, 'w') as file:
            for order in self.order_history:
                file.write(f"{order.customer.get_name()}, {', '.join(', '.join((product.get_id(), str(quantity))) for product,quantity in zip(order.products, order.quantities))}, {order.get_total_cost()}, {order.get_earned_rewards()}, {order.get_date_time()}\n")

# Operations class
class Operations:
    def __init__(self, customer_file, product_file, order_file):
        """Initializes the Operations class and reads customer, product and orders data from files."""
        self.records = Records()
        self.records.read_customers(customer_file)
        self.records.read_products(product_file)
        self.records.read_orders(order_file)

    # Validation methods
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
            raise InvalidProductError(f"The product {product_name} is not valid. Please enter a valid product name or ID.")
        return product
    
    def validate_quantity(self, quantity):
        """Validates that the quantity is a positive integer."""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise InvalidQuantityError("The quantity is not valid. Please enter a valid positive integer quantity.")
        except ValueError:
            raise InvalidQuantityError("The quantity is not valid. Please enter a valid positive integer quantity.")
        return quantity

    def validate_price(self, price):
        """Validates that the price is a positive number."""
        try:
            price = float(price)
            if price <= 0:
                raise InvalidPriceError("The price must be a positive number.")
        except ValueError:
            raise InvalidPriceError("The price is not valid. Please enter a valid positive number.")
        return price

    def validate_prescription(self, prescription):
        """Validates that the prescription input is either 'y' or 'n'."""
        if prescription not in ('y', 'n'):
            raise InvalidPrescriptionError("The answer is not valid. Please enter a valid answer.")
    
    def validate_positive_number(self, value):
        """Validates that the input is a positive number."""
        try:
            value = float(value)
            if value <= 0:
                raise ValueError("The value must be a positive number greater than 0.")
        except ValueError:
            raise InvalidRateError("The reward rate must be a valid positive number greater than 0.")
        return value

    # Menu methods
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
                product_names = input("Enter the product names or IDs (comma-separated):\n").split(",")
                product_names = [name.strip() for name in product_names]
                products = [self.validate_product(name) for name in product_names]
                break
            except InvalidProductError as e:
                print(e)
        
        while True:
            try:
                quantities = input("Enter the quantities (comma-separated):\n").split(',')
                quantities = [self.validate_quantity(qty.strip()) for qty in quantities]
                if len(products) != len(quantities):
                    raise InvalidQuantityError("The number of products and quantities must match.")
                break
            except InvalidQuantityError as e:
                print(e)

        for product in products:
            if product.requires_prescription() == 'y':
                while True:
                    try:
                        prescription_answer = input(f"The product {product.get_name()} require a doctor's prescription, do you have one? (y/n)\n").lower()
                        self.validate_prescription(prescription_answer)
                        if prescription_answer == "n":
                            print(f"Sorry. The product {product.get_name()} cannot be purchased without a doctor's prescription.")
                            products = [prod for prod in products if not prod.get_id() == product.get_id()]
                            quantities = [qty for prod, qty in zip(products, quantities) if not prod.get_id() == product.get_id()]
                            break
                        break
                    except InvalidPrescriptionError as e:
                        print(e)
                if prescription_answer == 'y':
                    break

        if products:
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
            order = Order(customer, products, quantities)

            # Calculate order details
            original_cost, discount, final_cost, reward_points = order.compute_cost()

            # Apply reward points deduction if applicable
            final_cost = order.apply_reward_points(final_cost)

            # Print receipt
            print("\n"+"-" * 40)
            print("Receipt".center(40))
            print("-" * 40)

            print(f"Name:\t {customer.get_name()}".expandtabs(20))

            for product, quantity in zip(products, quantities):
                print(f"Product:\t {product.get_name()}".expandtabs(20))
                print(f"Unit Price:\t {product.get_price():.2f} (AUD)".expandtabs(20))
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

            # Store order history
            order_history = OrderHistory(customer, products, quantities, final_cost, reward_points, datetime.datetime.now())
            self.records.order_history.append(order_history)

    def display_customers(self):
        """Prints a formatted list of all customers with their details."""
        self.records.list_customers()
    
    def display_products(self):
        """Prints a formatted list of all products with their details."""
        self.records.list_products()
    
    def add_update_products(self):
        """Handles the addition and updating of multiple products."""
        while True:
            try:
                product_details = input("Enter the product details (format: product price prescription), separated by commas:\n").split(",")
                product_details = [detail.strip() for detail in product_details]
                for detail in product_details:
                    name, price, prescription = detail.split()
                    price = self.validate_price(price)
                    self.validate_prescription(prescription)
                break
            except (InvalidPriceError, InvalidPrescriptionError) as e:
                print(e)
                print("Please re-enter the product details correctly.")
        
        for detail in product_details:
                    name, price, prescription = detail.split()
                    self.records.add_or_update_product(name, float(price), prescription)

    def adjust_basic_customer_reward_rate(self):
        """Adjusts the reward rate for all Basic customers."""
        while True:
            try:
                new_rate = input("Enter the new reward rate for all Basic customers:\n")
                new_rate = self.validate_positive_number(new_rate)
                BasicCustomer.set_reward_rate(new_rate)
                print(f"\nReward rate for all Basic customers has been updated to {new_rate * 100:.0f}%.")
                break
            except InvalidRateError as e:
                print(e)   

    def adjust_vip_customer_discount_rate(self):
        """Adjusts the discount rate for a VIP customer."""
        while True:
                customer_identifier = input("Enter the name or ID of the VIP customer:\n")
                vip_customer = self.records.find_customer(customer_identifier)
                if not isinstance(vip_customer, VIPCustomer):
                    print("Invalid customer. Please enter a valid VIP customer name or ID.")
                    continue
                break
          
        while True:
            try:
                new_rate = input("\nEnter the new discount rate for the VIP customer:\n")
                new_rate = self.validate_positive_number(new_rate)
                break
            except InvalidRateError as e:
                print(e)
        vip_customer.set_discount_rate(new_rate)

    def display_all_orders(self):
        """Prints a formatted list of all orders with their details."""
        self.records.list_orders()

    def display_customer_order_history(self):
        """Prints a formatted order list of a particular customer with their details."""
        while True:
                customer_identifier = input("Enter the name or ID of the customer:\n")
                customer = self.records.find_customer(customer_identifier)
                if not customer:
                    print("Invalid customer. Please enter a valid customer name or ID.")
                    continue
                break
       
    # Retrieve order history   
        order_history:OrderHistory = self.records.find_orders(customer)
    
    # Display order history
        print(f"\nThis is the order history of {customer.get_name()}.")
        print(f"\t{'Products':<30}{'Total Cost':<15}{'Earned Rewards':<15}".expandtabs(10))

        for i, order in enumerate(order_history, 1):
            products_info = ", ".join(f"{quantity} x {product.get_name()}" for product, quantity in zip(order.products, order.quantities))
            print(f"Order {i:<4}{products_info:<30}{order.total_cost:<15.2f}{order.earned_rewards:<15}") 

    def save_data(self):
        """Saves the data to the files"""
        customer_file, product_file, order_file = command_line_args()
        self.records.save_customers(customer_file)
        self.records.save_products(product_file)
        if os.path.isfile(order_file):
            self.records.save_orders(order_file)
        sys.exit()

    def display_menu(self):
        """Displays the program menu with available options."""
        print("\n"+"#" * 60)
        print("You can choose from the following options:")
        print("1: Make a purchase")
        print("2: Display existing customers")
        print("3: Display existing products")
        print("4: Add/update information of a product")
        print("5: Adjust the reward rate of all Basic customers")
        print("6: Adjust the discount rate of a VIP customer")
        print("7: Display all orders")
        print("8: Display a customer order history")
        print("0: Exit the program")   
        print("#" * 60)

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
            elif choice == '4':
                self.add_update_products()
            elif choice == '5':
                self.adjust_basic_customer_reward_rate()
            elif choice == '6':
                self.adjust_vip_customer_discount_rate()
            elif choice == '7':
                self.display_all_orders()
            elif choice == '8':
                self.display_customer_order_history()
            elif choice == '0':
                print("Exiting program...") # Exit message
                self.save_data() # Save data before terminate
            else:
                # Display error if enter incorrect input
                print("Invalid Choice. Please choose correct option.")

def command_line_args():
    """Reads file from command line arguments"""
    # default files
    customer_file = "customers.txt"
    product_file = "products.txt"
    order_file = "orders.txt"

    # If no argument passed through command line it checks for default files
    if len(sys.argv) == 1:
        if not os.path.isfile(customer_file):
            print("Error: Customer file not found in local directory.")
            sys.exit()

        if not os.path.isfile(product_file):
            print("Error: Product file not found in local directory.")
            sys.exit()

    # Show usage if invalid number of arguments passed
    elif len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python pharmacy.py <customer_file> <product_file> [order_file]")
        sys.exit()
   
    else:
        customer_file = sys.argv[1]
        product_file = sys.argv[2]
        order_file = order_file if len(sys.argv) == 3 else sys.argv[3]

    return customer_file, product_file, order_file

# Main program
if __name__ == "__main__":
    customer_file, product_file, order_file = command_line_args()
    operations = Operations(customer_file, product_file, order_file)
    operations.run()