from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def home_page(self):
        self.client.get("/")

    @task(2)
    def shop_page(self):
        self.client.get("/shop")

    @task(1)
    def about_page(self):
        self.client.get("/about")

    @task(1)
    def contact_page(self):
        self.client.get("/contact")

    @task(1)
    def revived_page(self):
        self.client.get("/revived")

    @task(1)
    def random_bike(self):
        # Simulate visiting a random bike detail page (IDs 1-20 as example)
        bike_id = random.randint(1, 20)
        self.client.get(f"/shop/{bike_id}")

    @task(1)
    def custom_bike(self):
        self.client.get("/custom-bike")
