import os
from flask import Flask, request, render_template, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from io import BytesIO
# Flask app setup
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
CORS(app, resources={r"/*": {"origins": "https://travel-trove-main.onrender.com"}})





MONGO_URI = os.environ.get("MONGO_URI", "https://travel-trove-main.onrender.com")  # Get from Render environment variables
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set.")


client = MongoClient('mongodb+srv://nightanon038:wV86jTZpkYJ1K6Qo@travel-trove.sdb1i.mongodb.net/?retryWrites=true&w=majority&appName=travel-trove')
serverSelectionTimeoutMS=50000,
db = client['travel_platform']
collection = db['posts']
fs = GridFS(db)


@app.route('/')
def home():
    return render_template('forum.html')  # Render your HTML template


@app.route('/posts', methods=['GET'])
def get_all_posts():
    try:
        posts = list(collection.find({}))
        for post in posts:
            # Convert ObjectId to string for JSON
            post["_id"] = str(post["_id"])
            if post.get("image_id"):
                post["image_url"] = f"{MONGO_URI}/file/{post['image_id']}"
            if post.get("video_id"):
                post["video_url"] = f"{MONGO_URI}/file/{post['video_id']}"
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/add_post', methods=['POST'])
def add_post():
    try:
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', "").split(",")  # Split tags
        upvote_post = request.form.get('upvote_post')
        downvote_post = request.form.get('downvote_post')
        

        # Handle file uploads
        image_file = request.files.get('images')
        video_file = request.files.get('videos')

        image_id = None
        video_id = None

        if image_file:
            image_id = fs.put(image_file, filename=image_file.filename,
                              content_type=image_file.content_type)
        if video_file:
            video_id = fs.put(video_file, filename=video_file.filename,
                              content_type=video_file.content_type)

        # Insert post into MongoDB
        post = {
            "_id": ObjectId(),
            "title": title,
            "content": content,
            "tags": tags,
            "image_id": str(image_id) if image_id else None,
            "video_id": str(video_id) if video_id else None,
            "upvotes": 0,   # Default upvotes to 0
            "downvotes": 0, # Default downvotes to 0
            "replies":[]
            
            
        }
        collection.insert_one(post)

        return jsonify({"message": "Post added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        # Retrieve file from GridFS
        file = fs.get(ObjectId(file_id))
        response = app.response_class(
            file.read(), content_type=file.content_type)
        response.headers["Content-Disposition"] = f"inline; filename={
            file.filename}"
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

@app.route('/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        # Delete file from GridFS
        fs.delete(ObjectId(file_id))
        return jsonify({"message": "File deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404
@app.route('/posts/<post_id>/upvote', methods=['POST'])
def upvote_post(post_id):
    try:
        collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"upvotes": 1}})
        return jsonify({"message": "Upvoted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/posts/<post_id>/downvote', methods=['POST'])
def downvote_post(post_id):
    try:
        collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"downvotes": 1}})
        return jsonify({"message": "Downvoted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/posts/reply/<post_id>', methods=['POST'])
def reply_post(post_id):
    try:
        # Use request.get_json() to parse JSON body
        data = request.get_json()
        content = data.get('content', '').strip()  # Get content and strip whitespace

        if not content:
            return jsonify({"status": "error", "message": "Reply content cannot be empty"}), 400
        
        reply = {"content": content}
        collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"replies": reply}})
        return jsonify({"message": "Reply added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Use a port like 10000 for Render
    app.run(host='0.0.0.0', port=port, debug=False) # Set debug to False for production