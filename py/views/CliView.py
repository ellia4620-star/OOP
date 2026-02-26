from typing import List
from py.models.Product import Product


class CliView:
    @staticmethod
    def print_menu() -> None:
        print("\n=== Inventory Menu ===")
        print("1) Add a product")
        print("2) Update product quantity")

        print("3) Show all products")
        print("4) Search a product by Product Code")
        print("5) Show products by category")

        print("6) AI inventory summary (Explain my inventory)")
        print("7) Ask the AI a question (Ollama)")
        print("8) AI recommendations for low stock (Ollama)")

        print("9) Show total inventory value")

        print("10) Delete a product by Product Code")
        print("11) Reset inventory (delete all products)")
        print("12) Exit")

    @staticmethod
    def show_message(message: str) -> None:
        print(message)

    @staticmethod
    def show_product(product: Product) -> None:
        print(product)

    @staticmethod
    def show_products_table(products: List[Product]) -> None:
        if not products:
            print("No products found.")
            return

        code_label = "Product Code"
        name_label = "Name"
        category_label = "Category"
        price_label = "Price"
        quantity_label = "Quantity"

        code_w = max(len(code_label), max(len(str(p.product_code)) for p in products))
        name_w = max(len(name_label), max(len(str(p.name)) for p in products))
        category_w = max(len(category_label), max(len(str(p.category)) for p in products))
        price_w = len(price_label)
        quantity_w = len(quantity_label)

        header = (
            f"{code_label.ljust(code_w)} | "
            f"{name_label.ljust(name_w)} | "
            f"{category_label.ljust(category_w)} | "
            f"{price_label.rjust(price_w)} | "
            f"{quantity_label.rjust(quantity_w)}"
        )
        print(header)
        print("-" * len(header))

        for p in products:
            price_str = f"{float(p.price):.2f}"
            qty_str = str(int(p.quantity))
            print(
                f"{str(p.product_code).ljust(code_w)} | "
                f"{str(p.name).ljust(name_w)} | "
                f"{str(p.category).ljust(category_w)} | "
                f"{price_str.rjust(price_w)} | "
                f"{qty_str.rjust(quantity_w)}"
            )