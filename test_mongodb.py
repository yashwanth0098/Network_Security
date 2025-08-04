from pymongo.mongo_client import MongoClient
from urllib.parse import quote_plus

# # Safely encode your password
# password = quote_plus("Yashwanth")  # Replace with your actual password

# Connection string
uri = f"mongodb+srv://yashwanth0098:Yashwanth@cluster0.b1ulvaa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create client and connect
client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)
