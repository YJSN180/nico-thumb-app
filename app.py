from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

OGP_TEMPLATE = """
<!doctype html>
<html lang=\"ja\">
<head>
    <meta charset=\"UTF-8\">
    <title>ニコニコ動画サムネ取得ツール</title>
    <meta property=\"og:title\" content=\"ニコニコ動画 サムネ取得ツール\" />
    <meta property=\"og:description\" content=\"デバイス制限付き動画のサムネイル画像を取得できます。\" />
    <meta property=\"og:image\" content=\"https://nico-thumb-app.onrender.com/static/ogp_nicovideo.png\" />
    <meta property=\"og:url\" content=\"https://nico-thumb-app.onrender.com/\" />
    <meta property=\"og:type\" content=\"website\" />
    <meta name=\"twitter:card\" content=\"summary_large_image\" />
</head>
<body>
    <p>このページはOGP対応用です。数秒後に移動します。</p>
    <script>window.location.href = '/tool';</script>
</body>
</html>
"""

HTML_TEMPLATE = """
<!doctype html>
<html lang=\"ja\">
<head>
    <meta charset=\"UTF-8\">
    <title>ニコニコ動画サムネイル取得</title>
</head>
<body>
    <h2>ニコニコ動画の動画IDを入力してください</h2>
    <form method=\"post\">
        <input type=\"text\" name=\"video_id\" placeholder=\"例: sm36735375\" required>
        <button type=\"submit\">サムネイル取得</button>
    </form>
    {% if thumbnail_url %}
        <h3>サムネイル画像:</h3>
        <img src=\"{{ thumbnail_url }}\" alt=\"サムネイル\">
    {% elif error %}
        <p>{{ error }}</p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def homepage():
    return OGP_TEMPLATE

@app.route('/tool', methods=['GET', 'POST'])
def tool():
    thumbnail_url = None
    error = None

    if request.method == 'POST':
        video_id = request.form['video_id'].strip()
        url = f'https://www.nicovideo.gay/watch/{video_id}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Accept-Language': 'ja,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            og_image = soup.find('meta', property='og:image')

            if og_image:
                thumbnail_url = og_image['content']
            else:
                error = 'サムネイルを取得できませんでした。'

        except requests.RequestException as e:
            error = f'エラーが発生しました: {e}'

    return render_template_string(HTML_TEMPLATE, thumbnail_url=thumbnail_url, error=error)

if __name__ == '__main__':
    app.run(debug=True)
