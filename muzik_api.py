from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

YOUTUBE_API_KEY = "AIzaSyBzQ7V_uivM772G71LYwGrfAUT6Wf8eWNw"

def youtube_api_search(query, max_results=10):
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults={max_results}&q={query}&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url)
    items = r.json().get("items", [])
    results = []
    for item in items:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        results.append({
            "id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })
    return results

@app.route('/ara', methods=['GET'])
def ara():
    q = request.args.get('q')
    if not q:
        return jsonify([])
    try:
        results = youtube_api_search(q)
        return jsonify(results)
    except Exception as e:
        return jsonify({'hata': str(e)}), 500

@app.route('/indir', methods=['GET'])
def indir():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'hata': 'ID gerekli'}), 400

    tempdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp"))
    os.makedirs(tempdir, exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(tempdir, filename)

    try:
        # Komut satırı yt-dlp ile indir
        import subprocess
        subprocess.run([
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "-x",
            "--audio-format", "mp3",
            "-o", filepath
        ], check=True)
        return send_file(filepath, as_attachment=True, download_name=f"{video_id}.mp3")
    except Exception as e:
        print('İndirme Hatası:', e)
        return jsonify({'hata': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
