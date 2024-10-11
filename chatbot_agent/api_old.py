from flask import Blueprint, jsonify, request

api = Blueprint('api', __name__)

songs = ["song1", "song2", "song3"]

@api.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        # DATA FROM ADD REQUEST -> {"data": "song_name"}
        data = request.json  
        song = data.get("data")

        # ADD SONG TO PLAYLIST HERE
        songs.append(song)

        return jsonify({"message": f"{song} was added to playlist!", "data": data})
    

@api.route('/remove', methods=['POST'])
def remove():
    if request.method == 'POST':
        # DATA FROM REMOVE REQUEST -> {"data": "song_name"}
        data = request.json  
        song = data.get("data")

        # REMOVE SONG FROM PLAYLIST HERE
        songs.remove(song)

        return jsonify({"message": f"{song} was removed from playlist!", "data": data})
    
@api.route('/clear', methods=['GET'])
def clear():
    if request.method == 'GET':
        # CLEAR PLAYLIST    
        return jsonify({"message": "Playlist was cleared!"})
    

@api.route('/playlist', methods=['GET'])
def playlist():
    if request.method == 'GET':
        return jsonify({"playlist": songs})