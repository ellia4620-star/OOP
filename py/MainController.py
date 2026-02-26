import sqlite3

from py.ai.InventoryAI import InventoryAI
from py.data.ProductRepository import ProductRepository
from py.models.Product import Product
from py.views.CliView import CliView


DEFAULT_LOW_STOCK_THRESHOLD = 5


def add_product(repo: ProductRepository) -> None:
    product_code = input("Product Code: ").strip()
    name = input("Name: ").strip()
    category = input("Category: ").strip() or "General"

    try:
        price = float(input("Price: ").strip())
        quantity = int(input("Quantity: ").strip())
    except ValueError:
        CliView.show_message("Please enter a valid number for price and quantity.")
        return

    try:
        repo.add_product(
            Product(
                product_code=product_code,
                name=name,
                category=category,
                price=price,
                quantity=quantity,
            )
        )
        CliView.show_message("Product added successfully.")
    except sqlite3.IntegrityError:
        CliView.show_message("That product code already exists. Please choose a different one.")


def update_quantity(repo: ProductRepository) -> None:
    product_code = input("Product Code to update: ").strip()
    try:
        new_quantity = int(input("New quantity: ").strip())
    except ValueError:
        CliView.show_message("Please enter a valid number for quantity.")
        return

    repo.update_quantity(product_code, new_quantity)
    CliView.show_message("Quantity updated.")


def show_all_products(repo: ProductRepository) -> None:
    CliView.show_products_table(repo.get_all_products())


def search_product(repo: ProductRepository) -> None:
    product_code = input("Product Code to search: ").strip()
    product = repo.find_by_product_code(product_code)

    if product is None:
        CliView.show_message("Product not found.")
        return

    CliView.show_product(product)


def show_by_category(repo: ProductRepository) -> None:
    categories = repo.get_categories()
    if not categories:
        CliView.show_message("No categories found.")
        return

    print("\nAvailable categories:")
    for c in categories:
        print(f"- {c}")

    category = input("Type a category name: ").strip()
    if not category:
        CliView.show_message("Category cannot be empty.")
        return

    products = repo.get_products_by_category(category)
    if not products:
        CliView.show_message("No products found in that category.")
        return

    CliView.show_products_table(products)


def ai_inventory_summary(repo: ProductRepository) -> None:
    threshold = DEFAULT_LOW_STOCK_THRESHOLD  # simple + easy to explain
    all_products = repo.get_all_products()
    low_stock = repo.get_low_stock(threshold)
    total_value = repo.get_total_inventory_value()

    CliView.show_message("Thinking... (Ollama)")
    summary = InventoryAI.inventory_summary(
        products=all_products,
        total_value=total_value,
        low_stock_products=low_stock,
        threshold=threshold,
        model="llama3",
    )

    print("\n--- Inventory Summary ---")
    print(summary)
    print("-------------------------\n")


def ask_ai_question(repo: ProductRepository) -> None:
    question = input("Type your question in English: ").strip()
    CliView.show_message("Thinking... (Ollama)")

    answer = InventoryAI.answer_question(repo.get_all_products(), question, model="llama3")
    print("\n--- AI Answer ---")
    print(answer)
    print("----------------\n")


def ai_low_stock_recommendations(repo: ProductRepository) -> None:
    raw = input(f"Low stock threshold (press Enter for {DEFAULT_LOW_STOCK_THRESHOLD}): ").strip()
    try:
        threshold = DEFAULT_LOW_STOCK_THRESHOLD if raw == "" else int(raw)
    except ValueError:
        CliView.show_message("Please enter a valid number.")
        return

    CliView.show_message("Thinking... (Ollama)")
    answer = InventoryAI.low_stock_recommendations(
        all_products=repo.get_all_products(),
        low_stock_products=repo.get_low_stock(threshold),
        threshold=threshold,
        model="llama3",
    )

    print("\n--- AI Recommendations ---")
    print(answer)
    print("-------------------------\n")


def show_inventory_value(repo: ProductRepository) -> None:
    total_value = repo.get_total_inventory_value()
    print(f"\nTotal inventory value: {total_value:.2f}\n")


def delete_product(repo: ProductRepository) -> None:
    product_code = input("Product Code to delete: ").strip()
    deleted = repo.delete_by_product_code(product_code)

    if deleted == 0:
        CliView.show_message("No such product.")
    else:
        CliView.show_message("Product deleted.")


def reset_inventory(repo: ProductRepository) -> None:
    confirm = input("This will delete ALL products. Are you sure? (y/n): ").strip().lower()
    if confirm == "y":
        repo.delete_all_products()
        CliView.show_message("Inventory reset.")
    else:
        CliView.show_message("Canceled.")


def main() -> None:
    repo = ProductRepository()

    while True:
        CliView.print_menu()
        choice = input("Choose an option (1-12): ").strip()

        if choice == "1":
            add_product(repo)
        elif choice == "2":
            update_quantity(repo)
        elif choice == "3":
            show_all_products(repo)
        elif choice == "4":
            search_product(repo)
        elif choice == "5":
            show_by_category(repo)
        elif choice == "6":
            ai_inventory_summary(repo)
        elif choice == "7":
            ask_ai_question(repo)
        elif choice == "8":
            ai_low_stock_recommendations(repo)
        elif choice == "9":
            show_inventory_value(repo)
        elif choice == "10":
            delete_product(repo)
        elif choice == "11":
            reset_inventory(repo)
        elif choice == "12":
            CliView.show_message("Goodbye.")
            break
        else:
            CliView.show_message("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()