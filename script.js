async function fetchPosts() {
    try {
        const response = await fetch('https://travel-trove-6y02.onrender.com//posts');
        const data = await response.json();
        
        console.log("Fetched data:", data); // Log the data to inspect it

        if (!data.trendingPosts || !data.recommendedPosts) {
            console.error("Error: Missing data fields", data);  // Log if fields are missing
            return;
        }
        
        
        
        displayPosts(data.trendingPosts, 'trendingPosts');
        displayPosts(data.recommendedPosts, 'recommendedPosts');
        
    } catch (error) {
        console.error("Error fetching posts:", error);
    }
}

function displayPosts(posts, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear existing content before adding new posts
    posts.forEach(post => {
        const postDiv = document.createElement('div');
        postDiv.className = 'post-card';
        postDiv.innerHTML = `
            <img src="${post.image_url}" alt="Post Image">
            <h2>${post.title}</h2>
            <p>Upvotes: ${post.upvotes}</p>
        `;
        container.appendChild(postDiv);
    });
}

// Fetch posts on page load
document.addEventListener('DOMContentLoaded', fetchPosts);
