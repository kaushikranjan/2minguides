class Products:

    def __init__(self):
        self.product_categories = {
            "Electronics": [("E001-LAPTOP", "MacBook Pro"), ("E002-PHONE", "iPhone 15"), ("E003-TABLET", "iPad Air"), ("E004-CAMERA", "Sony A7"), ("E005-HEADPHONES", "AirPods Pro")],
            "Clothing": [("C001-TSHIRT", "Nike Dri-Fit"), ("C002-JEANS", "Levi's 501"), ("C003-DRESS", "Zara Midi"), ("C004-JACKET", "North Face"), ("C005-SHOES", "Adidas Ultraboost")],
            "Books": [("B001-FICTION", "Harry Potter"), ("B002-NONFICTION", "Atomic Habits"), ("B003-EDUCATION", "Python Crash Course"), ("B004-CHILDREN", "The Gruffalo"), ("B005-REFERENCE", "Oxford Dictionary")],
            "Sports": [("S001-BALL", "Wilson Tennis"), ("S002-RACKET", "Babolat Pure"), ("S003-WEIGHTS", "Bowflex Dumbbells"), ("S004-MAT", "Lululemon Yoga"), ("S005-BAG", "Nike Gym Sack")],
            "Food": [("F001-SNACKS", "Doritos"), ("F002-CEREAL", "Cheerios"), ("F003-CANNED", "Campbell's Soup"), ("F004-FROZEN", "Ben & Jerry's"), ("F005-BAKERY", "Sara Lee")],
        }


    def strip_product_url(self, product_url: str) -> str:
        """
        Strips the base URL from a product URL to get just the product ID.
        
        Args:
            product_url (str): The full product URL
            
        Returns:
            str: Just the product ID from the URL
        """
        base_url = "https://www.shoptillyoudrop.com/product/"
        return product_url.replace(base_url, "")
    
    def get_random_product_url(self) -> str:
        """
        Returns a random product URL from the available products.
        
        Returns:
            str: A URL string in the format 'https://www.shoptillyoudrop.com/product/{product_id}'
        """
        import random
        all_products = self.get_products()
        (random_product_id, _) = random.choice(all_products)
        return f"https://www.shoptillyoudrop.com/product/{random_product_id}"
    
    def get_products(self):
        """
        Returns a list of all product IDs across all categories.
        
        Returns:
            list: A list of strings containing all product IDs from all categories.
                 Example: ['E001-LAPTOP', 'E002-PHONE', ..., 'A005-WIPERS']
        """
        all_products = []
        for category_products in self.product_categories.values():
            for product_id, _ in category_products:
                all_products.append(product_id)
        return all_products


    def get_product_category(self, product_id: str) -> tuple:
        """
        Returns the category and product name for a given product ID.
        
        Args:
            product_id (str): The product ID to look up
            
        Returns:
            tuple: A tuple containing (category_name, product_name) for the given product ID
        """
        for category, products in self.product_categories.items():
            for prod_id, prod_name in products:
                if prod_id == product_id:
                    return (category, (prod_id, prod_name))
        return (None, (None, None))

  
    def get_products(self):
        """
        Returns a list of all product IDs across all categories.
        
        Returns:
            list: A list of strings containing all product IDs from all categories.
                 Example: ['E001-LAPTOP', 'E002-PHONE', ..., 'A005-WIPERS']
        """
        all_products = []
        for category_products in self.product_categories.values():
            all_products.extend(category_products)
        return all_products