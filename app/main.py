from flask import Flask, render_template, request
from flask_caching import Cache
import requests
from bs4 import BeautifulSoup
import os


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Configure caching
app.config['CACHE_TYPE'] = 'filesystem'  # Use the filesystem cache
app.config['CACHE_DIR'] = '/app/cache'  # Directory for storing cache files
app.config['CACHE_DEFAULT_TIMEOUT'] = 86400  # Cache timeout: 1 hour (3600 seconds)
cache = Cache(app)

# Create cache directory if it doesn't exist
if not os.path.exists(app.config['CACHE_DIR']):
    os.makedirs(app.config['CACHE_DIR'])

def get_roomclip_items(tag_id):
    base_url = "https://roomclip.jp"
    item_data = []

    page = 1
    while True:
        tag_url = f"{base_url}/tag/{tag_id}?page={page}"

        response = requests.get(tag_url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select("div.tag-cards .card")

        if not items:
            break

        for item in items:
            item_url = f"{base_url}{item.select_one('a')['href']}"
            item_image = item.select_one(".card_photo_image")["src"]
            item_tags = [tag.text.strip() for tag in item.select(".tags .tag .label")]
            item_user_name = item.select_one(".card_user_label").text.strip()
            item_user_image = item.select_one(".card_user_image")["src"]
            item_user_link = f"{base_url}{item.select_one('.card_user_link')['href']}"
            item_data.append((item_url, item_image, item_tags, item_user_name, item_user_image, item_user_link))

        page += 1

    return item_data


@app.route("/", methods=["GET", "POST"])
def index():
    grouped_items = {}
    item_count = 0
    user_count = 0
    tag_id = request.args.get("tag_id") or request.form.get("tag_id")
    tag_filter = request.args.get("tag_filter") or request.form.get("tag_filter")

    if tag_id:
        items = get_cached_roomclip_items(tag_id)

        # タグフィルター
        if tag_filter:
            items = [item for item in items if tag_filter in item[2]]
        else:
            tag_filter = ""

        item_count = len(items)

        for item in items:
            if item[5] not in grouped_items:
                grouped_items[item[5]] = []
            grouped_items[item[5]].append(item)

        user_count = len(grouped_items)

    return render_template("index.html", grouped_items=grouped_items, item_count=item_count, user_count=user_count, tag_id=tag_id, tag_filter=tag_filter)

# A wrapper function for caching
@cache.cached()
def get_cached_roomclip_items(tag_id):
    cache_filename = f"cache/{tag_id}_roomclip_items.pickle"

    if os.path.exists(cache_filename):
        file_mtime = os.path.getmtime(cache_filename)
        if (time.time() - file_mtime) / 3600 < 24:  # 24時間以内にキャッシュされた場合
            try:
                with open(cache_filename, "rb") as f:
                    return pickle.load(f)
            except (EOFError, IOError):
                pass

    items = get_roomclip_items(tag_id)
    with open(cache_filename, "wb") as f:
        pickle.dump(items, f)

    return items

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
