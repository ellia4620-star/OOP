import sqlite3
from typing import List, Optional

from py.models.Product import Product


class ProductRepository:
    def __init__(self, db_path: str = "inventory.db") -> None:
        self.db_path = db_path
        self._create_table_if_needed()
        self._migrate_sku_to_product_code_if_needed()
        self._ensure_category_column_if_needed()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _table_exists(self) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
            )
            return cur.fetchone() is not None

    def _get_columns(self) -> List[str]:
        if not self._table_exists():
            return []
        with self._connect() as conn:
            cur = conn.execute("PRAGMA table_info(products)")
            return [row[1] for row in cur.fetchall()]

    def _create_table_if_needed(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'General',
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def _migrate_sku_to_product_code_if_needed(self) -> None:
        """If an old schema exists with 'sku', migrate it to 'product_code'."""
        cols = self._get_columns()
        if "sku" in cols and "product_code" not in cols:
            with self._connect() as conn:
                conn.execute("BEGIN")

                # Create new table with the new schema
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_code TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL DEFAULT 'General',
                        price REAL NOT NULL,
                        quantity INTEGER NOT NULL
                    )
                    """
                )

                # Copy data from old table (sku -> product_code)
                if "category" in cols:
                    conn.execute(
                        """
                        INSERT INTO products_new (product_code, name, category, price, quantity)
                        SELECT sku, name, COALESCE(category, 'General'), price, quantity
                        FROM products
                        """
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO products_new (product_code, name, category, price, quantity)
                        SELECT sku, name, 'General', price, quantity
                        FROM products
                        """
                    )

                # Replace old table
                conn.execute("DROP TABLE products")
                conn.execute("ALTER TABLE products_new RENAME TO products")

                conn.commit()

    def _ensure_category_column_if_needed(self) -> None:
        """If category is missing for some reason, add it."""
        cols = self._get_columns()
        if "category" not in cols:
            with self._connect() as conn:
                conn.execute("ALTER TABLE products ADD COLUMN category TEXT NOT NULL DEFAULT 'General'")
                conn.commit()

    # CRUD
    def add_product(self, product: Product) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO products (product_code, name, category, price, quantity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (product.product_code, product.name, product.category, product.price, product.quantity),
            )
            conn.commit()

    def get_all_products(self) -> List[Product]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT product_code, name, category, price, quantity
                FROM products
                ORDER BY category, name
                """
            )
            rows = cur.fetchall()

        return [
            Product(product_code=pc, name=name, category=cat, price=price, quantity=qty)
            for pc, name, cat, price, qty in rows
        ]

    def find_by_product_code(self, product_code: str) -> Optional[Product]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT product_code, name, category, price, quantity
                FROM products
                WHERE product_code = ?
                """,
                (product_code,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        pc, name, cat, price, qty = row
        return Product(product_code=pc, name=name, category=cat, price=price, quantity=qty)

    def update_quantity(self, product_code: str, new_quantity: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE products SET quantity = ? WHERE product_code = ?",
                (new_quantity, product_code),
            )
            conn.commit()

    def get_categories(self) -> List[str]:
        with self._connect() as conn:
            cur = conn.execute("SELECT DISTINCT category FROM products ORDER BY category")
            return [row[0] for row in cur.fetchall()]

    def get_products_by_category(self, category: str) -> List[Product]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT product_code, name, category, price, quantity
                FROM products
                WHERE category = ?
                ORDER BY name
                """,
                (category,),
            )
            rows = cur.fetchall()

        return [
            Product(product_code=pc, name=name, category=cat, price=price, quantity=qty)
            for pc, name, cat, price, qty in rows
        ]

    def get_low_stock(self, threshold: int) -> List[Product]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT product_code, name, category, price, quantity
                FROM products
                WHERE quantity <= ?
                ORDER BY quantity ASC, category, name
                """,
                (threshold,),
            )
            rows = cur.fetchall()

        return [
            Product(product_code=pc, name=name, category=cat, price=price, quantity=qty)
            for pc, name, cat, price, qty in rows
        ]

    def delete_by_product_code(self, product_code: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM products WHERE product_code = ?",
                (product_code,),
            )
            conn.commit()
            return cur.rowcount

    def delete_all_products(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM products")
            conn.commit()

    def get_total_inventory_value(self) -> float:
        with self._connect() as conn:
            cur = conn.execute("SELECT SUM(price * quantity) FROM products")
            result = cur.fetchone()[0]
        return float(result) if result is not None else 0.0