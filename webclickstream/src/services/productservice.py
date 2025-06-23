from src.utils.products import Products

class ProductService:
    def __init__(self):
        self.products = Products()
        
    def get_product_details(self, product_id: str) -> dict:
        """
        Get product name and segment for a given product ID.
        
        Args:
            product_id (str): The product ID to look up
            
        Returns:
            dict: A dictionary containing the product details with keys:
                - product_id (str): The unique identifier of the product
                - product_name (str): The name of the product
                - product_segment (str): The category/segment the product belongs to
        """
        
        # Get product segment and name from product id
        (product_segment, (_, product_name)) = self.products.get_product_category(product_id)
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "product_segment": product_segment
        }
