import random
from faker import Faker
        

class UserService:
    def __init__(self):
        # Define possible values for user attributes
        self.fake = Faker('en_IN')
        
    def generate_user_attributes(self, user_id: str):
        """
        Generate random age, gender and location for a given user ID.
        
        Args:
            user_id (str): The user ID to generate attributes for
            
        Returns:
            dict: A dictionary containing the generated user attributes
        """
        # Use user_id as seed for consistent generation
        random.seed(hash(user_id))
        
        # Generate random attributes
        age = self.fake.random_int(min=18, max=80)
        gender = self.fake.random_element(elements=["Male", "Female"])
        location = self.fake.city()
        
        return {
            "user_id": user_id,
            "user_age": age,
            "user_gender": gender,
            "user_location": location
        }
