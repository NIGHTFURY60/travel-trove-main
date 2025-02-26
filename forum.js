document.addEventListener("DOMContentLoaded", () => {
    const forumPostsContainer = document.getElementById("forumPosts");
    const postPopup = document.getElementById("postPopup");
    const openPostButton = document.getElementById("openPostButton");
    const closePostButton = document.getElementById("closePostButton");
    const postForm = document.getElementById("postForm");
    const postTemplate = document.getElementById("postTemplate");
    
    const API_BASE_URL = "https://travel-trove-6y02.onrender.com/"; // Update with your backend URL

    async function fetchPosts() {
        try {
            const response = await fetch(`${API_BASE_URL}/posts`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const posts = await response.json();
            
            // Get the container where posts should be added
            const forumPostsContainer = document.getElementById("forumPosts");
            if (!forumPostsContainer) throw new Error("forumPostsContainer not found in the DOM");
    
            // Clear previous posts
            forumPostsContainer.innerHTML = "";
    
            console.log("Fetched Posts:", posts);
    
            posts.forEach(renderPost);
    
        } catch (error) {
            console.error("Error fetching posts:", error);
        }
    }
    
    
  
    

    function renderPost(post) {
        const postElement = postTemplate.content.cloneNode(true);
        const postContainer = postElement.querySelector(".post");
        postContainer.setAttribute("data-post-id", post._id || "");

        postElement.querySelector(".post-title").textContent = post.title;
        postElement.querySelector(".post-content").textContent = post.content;
        postElement.querySelector(".post-tags").textContent = post.tags ? post.tags.join(", ") : "";
        postElement.querySelector(".post-upvotes").textContent = post.upvotes || 0;
        postElement.querySelector(".post-downvotes").textContent = post.downvotes || 0;

        const mediaContainer = postElement.querySelector(".post-media");
        if (post.image_url) {
            const img = document.createElement("img");
            img.src = post.image_url;
            img.alt = "Post Image";
            img.style.width = "100%";
            mediaContainer.appendChild(img);
        }
        if (post.video_url) {
            const video = document.createElement("video");
            video.src = post.video_url;
            video.controls = true;
            video.style.width = "100%";
            mediaContainer.appendChild(video);
        }

        postElement.querySelector(".upvote-btn").addEventListener("click", () => handleVote(post._id, "upvote"));
        postElement.querySelector(".downvote-btn").addEventListener("click", () => handleVote(post._id, "downvote"));

        // Add event listener for submit reply button
        const replyField = postElement.querySelector(".reply-field textarea");
        postElement.querySelector(".submit-reply-btn").addEventListener("click", async () => {
            const replyContent = replyField.value.trim();
            if (replyContent === "") {
                alert("Reply content cannot be empty.");
                return;
            }
            try {
                const response = await fetch(`${API_BASE_URL}/posts/reply/${post._id}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ content: replyContent })  // Send as JSON
                });
                if (response.ok) {
                    alert("Reply added successfully!");
                    replyField.value = ''; // Clear the reply input
                    fetchPosts(); // Reload posts to reflect the new reply
                } else {
                    const errorData = await response.json();
                    alert(`Error adding reply: ${errorData.message}`);
                }
            } catch (error) {
                console.error("Error adding reply:", error);
                alert("Failed to add reply. Please try again.");
            }
        });

        // Toggle replies visibility
        const repliesContainer = postElement.querySelector(".replies-container");
        const repliesList = postElement.querySelector(".replies");
        const toggleRepliesButton = postElement.querySelector(".toggle-replies-btn");

        toggleRepliesButton.addEventListener("click", () => {
            if (repliesContainer.style.display === "none" || repliesContainer.style.display === "") {
                repliesContainer.style.display = "block";
                toggleRepliesButton.textContent = "Hide Replies";
                // Render replies if they exist
                repliesList.innerHTML = ""; // Clear previous replies
                if (post.replies) {
                    post.replies.forEach(reply => {
                        const replyElement = document.createElement("div");
                        replyElement.className = "reply";
                        replyElement.textContent = reply.content;
                        repliesList.appendChild(replyElement);
                    });
                }
            } else {
                repliesContainer.style.display = "none";
                toggleRepliesButton.textContent = "Show Replies";
            }
        });

        forumPostsContainer.appendChild(postElement);
    }

    async function handleVote(postId, type) {
        try {
            const response = await fetch(`${API_BASE_URL}/posts/${postId}/${type}`, {
                method: "POST"
            });
            if (response.ok) {
                fetchPosts(); // Reload posts to reflect the updated votes
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.message}`);
            }
        } catch (error) {
            console.error(`Error handling ${type}:`, error);
            alert(`Failed to ${type}. Please try again.`);
        }
    }

    openPostButton.addEventListener("click", () => {
        postPopup.style.display = "block";
    });

    closePostButton.addEventListener("click", () => {
        postPopup.style.display = "none";
    });

    postForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(postForm);
        if (!formData.has('title') || !formData.has('content')) {
            alert("Please fill in all required fields.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/add_post`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                alert("Post created successfully!");
                postPopup.style.display = "none";
                postForm.reset();
                fetchPosts(); // Reload posts
            } else {
                const errorData = await response.json();
                alert(`Error creating post: ${errorData.message}`);
            }
        } catch (error) {
            console.error("Error creating post:", error);
            alert("Failed to create post. Please try again.");
        }
    });

    fetchPosts();
});
