import os
import json
import openai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from utils.fetch_weather import preprocess_weather_data
from utils.embedding_utils import get_embedding

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure OpenAI API key is set
openai.api_key = OPENAI_API_KEY
if not openai.api_key:
    raise ValueError("OpenAI API key not set. Please check your environment variables or .env file.")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

INDEX_NAME = "weather-data-index"
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
else:
    print(f"Index '{INDEX_NAME}' already exists.")

index = pc.Index(INDEX_NAME)

def store_weather_data(location):
    """
    Stores weather data in Pinecone index.
    """
    print(f"Processing weather data for location: {location}")
    preprocessed_data = preprocess_weather_data(location)
    if not preprocessed_data:
        print(f"Failed to preprocess weather data for {location}")
        return

    # Include 'text' in metadata
    full_metadata = preprocessed_data["metadata"]
    full_metadata["text"] = preprocessed_data["text"]

    # Generate embedding
    embedding = get_embedding(preprocessed_data["text"])
    if not embedding:
        print(f"Failed to generate embedding for {location}")
        return

    # Upsert data into Pinecone
    try:
        index.upsert(
            vectors=[
                {
                    "id": f"weather-{preprocessed_data['metadata']['location']}",
                    "values": embedding,
                    "metadata": full_metadata
                }
            ]
        )
        print(f"Weather data for {location} stored successfully.")
    except Exception as e:
        print(f"Error upserting data for {location}: {e}")

def batch_store_weather_data(locations):
    """
    Processes and stores weather data for a batch of locations.
    """
    for location in locations:
        store_weather_data(location)

if __name__ == "__main__":
    # Example usage
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "Austin", "Jacksonville", "Fort Worth", "Columbus", "Indianapolis",
        "Charlotte", "San Francisco", "Seattle", "Denver", "Washington",
        "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City",
        "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore",
        "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento",
        "Mesa", "Kansas City", "Atlanta", "Omaha", "Colorado Springs",
        "Raleigh", "Miami", "Virginia Beach", "Oakland", "Minneapolis",
        "Tulsa", "Arlington", "Tampa", "New Orleans", "Wichita", 
        "Cleveland", "Bakersfield", "Aurora", "Anaheim", "Honolulu",
        "Santa Ana", "Riverside", "Corpus Christi", "Lexington", "Stockton",
        "Henderson", "Saint Paul", "St. Louis", "Cincinnati", "Pittsburgh"]
    
    batch_store_weather_data(locations)







