from dataclasses import dataclass


@dataclass
class Product:
    product_code: str
    name: str
    category: str
    price: float
    quantity: int

    def __str__(self) -> str:
        return (
            f"Product Code: {self.product_code} | "
            f"Name: {self.name} | "
            f"Category: {self.category} | "
            f"Price: {self.price:.2f} | "
            f"Quantity: {self.quantity}"
        )