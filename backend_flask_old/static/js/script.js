ChatWidget({
    name: "Chatbot",
    serverUrl: "http://127.0.0.1:5000",
    useFeedback: true,
    useLogin: true,
  }, "customContainerId");

// Function to update the playlist UI
function updatePlaylistUI(updatedPlaylist) {
  // Clear the existing list
  const playlistUl = document.querySelector(".playlist ul");
  playlistUl.innerHTML = "";

  // Add updated songs
  updatedPlaylist.songs.forEach(song => {
    const li = document.createElement("li");
    li.innerHTML = `${song.title} by ${song.artist} (Album: ${song.album}, Year: ${song.year}) 
                <form action="/remove_song/${song.id}" method="post" style="display:inline;">
                    <button type="submit">Remove</button>
                </form>`;
    playlistUl.appendChild(li);
  });
}

// Function to add a song asynchronously
document.getElementById("addSongForm").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent default form submission

  // Get the selected song ID
  const songId = document.getElementById("songSelect").value;

  // Send AJAX request to the server to add the song
  fetch("{{ url_for('main.add_song') }}", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "song_id=" + songId,
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Song successfully added, you can now update the playlist in the DOM
        updatePlaylistUI(data.updated_playlist);  // Call a function to refresh the playlist UI
      } else {
        alert("Failed to add the song.");
      }
    });
});