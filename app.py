from flask import Flask, render_template, request, redirect, url_for, Response
import threading
import time
import requests
from io import BytesIO
import random

app = Flask(__name__)

# ---- Username Remover Class ----
class UsernameRemover:
    def __init__(self):
        self.total_changes = 150
        self.change_count = 0
        self.error_count = 0

    def generate_random_csrf(self):
        return ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=32))

    def download_image(self, url):
        try:
            image_response = requests.get(url)
            if image_response.status_code != 200:
                return None
            return BytesIO(image_response.content)
        except:
            return None

    def change_profile_picture(self, sessionid, url_img):
        url = 'https://www.instagram.com/accounts/web_change_profile_picture/'
        csrf_token = self.generate_random_csrf()
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/edit/",
            "X-CSRFToken": csrf_token,
            "Cookie": f"sessionid={sessionid}; csrftoken={csrf_token};"
        }
        try:
            files = self.download_image(url_img)
            if not files:
                return False
            response = requests.post(url, headers=headers, files={"profile_pic": ("profile.jpg", files, "image/jpeg")})
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get("status") == "ok"
                except:
                    return True
            else:
                return False
        except:
            return False

    def run_process(self, sessionid, progress_callback=None):
        pfp_urls = [
            'https://i.pinimg.com/736x/c6/65/37/c6653741ca1dac5c2ebcfeb7eb8f07c4.jpg',
            'https://i.pinimg.com/736x/c6/44/90/c64490f7c298cbc83bf62be0913cb216.jpg',
            'https://i.pinimg.com/736x/6d/f6/34/6df63455058f150ec0ec785e1d67ef31.jpg',
            'https://i.pinimg.com/736x/7a/38/05/7a3805f9619a344e61a297e091fd41fa.jpg'
        ]

        self.change_count = 0
        self.error_count = 0

        while self.change_count < self.total_changes:
            for url in pfp_urls:
                if self.change_count >= self.total_changes:
                    break
                success = self.change_profile_picture(sessionid, url)
                if success:
                    self.change_count += 1
                else:
                    self.error_count += 1
                if progress_callback:
                    progress_callback(self.change_count, self.error_count, self.total_changes)
                time.sleep(2)  # simulate delay

# ---- Flask app ----
remover = UsernameRemover()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    sessionid = request.form.get('sessionid')
    if not sessionid:
        return redirect(url_for('index'))

    def background_task():
        remover.run_process(sessionid)

    threading.Thread(target=background_task).start()
    return redirect(url_for('progress'))

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/progress_stream')
def progress_stream():
    def generate():
        last_change = -1
        while remover.change_count < remover.total_changes:
            if remover.change_count != last_change:
                last_change = remover.change_count
                yield f"data: {remover.change_count},{remover.error_count},{remover.total_changes}\n\n"
            time.sleep(1)
        yield f"data: {remover.change_count},{remover.error_count},{remover.total_changes}\n\n"
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)