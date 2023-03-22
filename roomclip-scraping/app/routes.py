from flask import Blueprint, render_template, request
import requests
from bs4 import BeautifulSoup
import pickle
from datetime import datetime, timedelta
from models import CacheItem
from werkzeug.security import check_password_hash
from app import db, auth, users


def get_roomclip_items(tag_id, cached_items=None):
    base_url = "https://roomclip.jp"
    item_data = []
    new_items = []
    first_cached_item = None

    page = 1

    if cached_items:
        first_cached_item = cached_items[0]

    while True:
        tag_url = f"{base_url}/tag/{tag_id}?sort=new&page={page}"

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

            # キャッシュと最新データの比較
            if cached_items and item_data == first_cached_item:
                return new_items + cached_items
            new_items.append(item_data)

        page += 1

    return new_items


def get_cached_roomclip_items(tag_id):
    cache_item = CacheItem.query.filter_by(tag_id=tag_id).order_by(CacheItem.timestamp.desc()).first()

    # キャッシュしてから1日経っていなかったら、DBからデータを取得する
    if cache_item and (datetime.utcnow() - cache_item.timestamp) < timedelta(days=1):
        items = pickle.loads(cache_item.data)
    else:
        items = get_roomclip_items(tag_id)

        # 新しくデータを取得した場合は、DBを更新
        cache_item = CacheItem(tag_id=tag_id, data=pickle.dumps(items))
        db.session.add(cache_item)
        db.session.commit()

    return items


main = Blueprint("main", __name__)


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@main.route("/", methods=["GET", "POST"])
@auth.login_required
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
    else:
        tag_id = ''
        tag_filter = ''

    return render_template("index.html", grouped_items=grouped_items, item_count=item_count, user_count=user_count, tag_id=tag_id, tag_filter=tag_filter)