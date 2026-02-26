Inventory Management System (OOP – Python)

This project is an Object-Oriented Inventory Management System developed in Python. The purpose of the program is to manage products in an inventory using a command-line interface (CLI) while applying core Object-Oriented Programming (OOP) principles such as encapsulation, separation of concerns, and modular design.

The system allows the user to add new products, update product quantities, display all products, search for products by SKU, delete specific products, and reset the entire inventory. The program is structured in a clear and organized way, separating models, data handling, views, controllers, and services into different modules.

The Product class represents a single product in the inventory and contains attributes such as SKU, name, price, and quantity. The ProductRepository class is responsible for managing the collection of products, including adding, updating, deleting, and retrieving product data. The CliView class handles all user interaction through the command line, including displaying menus and reading user input. The MainController class coordinates between the view and the data layer and controls the overall program flow.

An optional AI component is included in the project. The InventoryAI module can connect to a local Ollama server in order to analyze inventory data and return intelligent insights, such as summaries or recommendations. If the AI service is not available, the main inventory system continues to function normally without it.

To run the program, Python 3 must be installed. The program is executed by running the main.py file from the project’s root directory using the command line. The project was developed using Visual Studio Code and follows standard Python project structure conventions.

This project demonstrates practical use of Object-Oriented Programming concepts, clean code organization, and basic integration of external services, and was created as part of an academic assignment.
