from flask import Flask, jsonify, render_template, send_file 
from flask_cors import CORS
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
import gridfs
import io
import random
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
CORS(app, resources={r"/*": {"origins": "https://travel-trove-main.onrender.com"}})


# Connect to MongoDB Atlas
client = MongoClient('mongodb+srv://nightanon038:wV86jTZpkYJ1K6Qo@travel-trove.sdb1i.mongodb.net/?retryWrites=true&w=majority&appName=travel-trove')
serverSelectionTimeoutMS=50000,
db = client['travel_platform']  # Database name
posts_collection = db['posts']
fs = gridfs.GridFS(db)

MONGO_URI = os.environ.get("MONGO_URI")  # Get from Render environment variables
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set.")

client = MongoClient('mongodb+srv://nightanon038:wV86jTZpkYJ1K6Qo@travel-trove.sdb1i.mongodb.net/?retryWrites=true&w=majority&appName=travel-trove')
db = client['travel_platform']
posts_collection = db['posts']
fs = GridFS(db)  # Use GridFS directly


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        # Fetch all posts from MongoDB
        all_posts = list(posts_collection.find())

        if not all_posts:
            return jsonify({'message': 'No posts found in database'}), 404
        # Trending posts = Top 5 highest upvoted
        trending_posts = sorted(all_posts, key=lambda x: x.get('upvotes', 0), reverse=True)[:5]
        
        # Recommended posts = 5 random posts
        all_posts = list(posts_collection.find())
        recommended_posts = random.sample(all_posts, min(3, len(all_posts)))

        # Convert MongoDB ObjectId to string
        for post in trending_posts + recommended_posts:
            post['_id'] = str(post['_id'])
            if 'image_id' in post:
                post["image_url"] = f"https://your-app.onrender.com/file/{post['image_id']}"
            else:
                post['image_url'] = "/static/default.jpg"  # Default placeholder
         # Check if both fields exist before sending response
        if trending_posts and recommended_posts:
            response = {'trendingPosts': trending_posts, 'recommendedPosts': recommended_posts}
            print("Response Sent to Frontend:", response)  # Debugging output
            return jsonify(response)
        else:
         return jsonify({'trendingPosts': trending_posts, 'recommendedPosts': recommended_posts})
    except Exception as e:
        print("Error:", e)  # Print error to terminal
        return jsonify({'message': str(e)}), 500

@app.route('/image/<image_id>')
def get_image(image_id):
    """Fetch image from GridFS and return as a response."""
    try:
        image_file = fs.get(ObjectId(image_id))  # Get image from GridFS
        return send_file(io.BytesIO(image_file.read()), mimetype="image/jpeg")
    except Exception as e:
        return jsonify({'message': 'Image not found'}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Use a port like 10000 for Render
    app.run(host='0.0.0.0', port=port, debug=False) # Set debug=True while testing locally