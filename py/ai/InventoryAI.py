import json
import urllib.error
import urllib.request
from typing import List

from py.models.Product import Product


class InventoryAI:
    @staticmethod
    def _call_ollama(
        prompt: str,
        model: str = "llama3",
        url: str = "http://localhost:11434/api/generate",
        timeout_seconds: int = 120,
    ) -> str:
        payload = {"model": model, "prompt": prompt, "stream": False}
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
                result = json.loads(body)
                response_text = (result.get("response") or "").strip()
                return response_text or "The model returned an empty response."
        except urllib.error.URLError:
            return (
                "Could not connect to Ollama.\n"
                "Please make sure Ollama is running and the model is installed."
            )
        except Exception as exc:
            return f"Unexpected error while contacting Ollama: {exc}"

    @staticmethod
    def _format_inventory(products: List[Product]) -> str:
        if not products:
            return "(No products found.)"
        return "\n".join(
            f"- Product Code: {p.product_code}, Name: {p.name}, Category: {p.category}, Price: {p.price}, Quantity: {p.quantity}"
            for p in products
        )

    @staticmethod
    def inventory_summary(
        products: List[Product],
        total_value: float,
        low_stock_products: List[Product],
        threshold: int,
        model: str = "llama3",
    ) -> str:
        all_text = InventoryAI._format_inventory(products)
        low_text = InventoryAI._format_inventory(low_stock_products)

        prompt = (
            "You are an inventory assistant for a small store.\n"
            "Your job is to explain the inventory in a simple, friendly way.\n\n"
            "Rules:\n"
            "- Answer in simple English.\n"
            "- Use short bullet points.\n"
            "- Do NOT invent data.\n"
            "- Mention Product Codes when referencing products.\n\n"
            f"Total inventory value: {total_value:.2f}\n"
            f"Low stock definition: Quantity <= {threshold}\n\n"
            f"Full product list:\n{all_text}\n\n"
            f"Low stock list:\n{low_text}\n\n"
            "Write a short summary with:\n"
            "1) Overall status (1-2 bullets)\n"
            "2) What needs attention now (low stock)\n"
            "3) One practical tip\n"
        )
        return InventoryAI._call_ollama(prompt=prompt, model=model)

    @staticmethod
    def answer_question(products: List[Product], question: str, model: str = "llama3") -> str:
        inventory_text = InventoryAI._format_inventory(products)
        user_question = (question or "").strip()
        if not user_question:
            return "Please type a question."

        prompt = (
            "You are an inventory assistant for a small store.\n"
            "You MUST answer only based on the product list provided.\n\n"
            "Rules:\n"
            "- Answer in simple English.\n"
            "- Be helpful and friendly.\n"
            "- Use bullet points when possible.\n"
            "- Do not invent products or data that are not listed.\n"
            "- If the question cannot be answered from the list, say what is missing.\n"
            "- Before answering, scan the entire product list carefully.\n"
            "- When you mention a product, include its Product Code.\n\n"
            f"Product list:\n{inventory_text}\n\n"
            f"User question:\n{user_question}"
        )
        return InventoryAI._call_ollama(prompt=prompt, model=model)

    @staticmethod
    def low_stock_recommendations(
        all_products: List[Product],
        low_stock_products: List[Product],
        threshold: int,
        model: str = "llama3",
    ) -> str:
        all_text = InventoryAI._format_inventory(all_products)
        low_text = InventoryAI._format_inventory(low_stock_products)

        prompt = (
            "You are an inventory assistant for a small store.\n"
            "You received a full product list and a low-stock list.\n\n"
            f"Low stock means Quantity <= {threshold}.\n\n"
            "Tasks:\n"
            "1) List only the low-stock products.\n"
            "2) Suggest reorder amounts (a simple number) for each low-stock product.\n"
            "3) Group suggestions by category.\n"
            "4) Add 2 short tips.\n\n"
            "Rules:\n"
            "- Answer in simple English.\n"
            "- Use bullet points.\n"
            "- Do not invent products that are not listed.\n"
            "- If low-stock list is empty, say it clearly.\n"
            "- When you mention a product, include its Product Code.\n"
            "- Before answering, scan the lists carefully.\n\n"
            f"Full product list:\n{all_text}\n\n"
            f"Low-stock list:\n{low_text}"
        )
        return InventoryAI._call_ollama(prompt=prompt, model=model)