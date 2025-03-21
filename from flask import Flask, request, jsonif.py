from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import openai
import os

# 初始化 Flask 应用
app = Flask(__name__)

# 设置 OpenAI API 密钥
openai.api_key = os.getenv('OPENAI_API_KEY')  # 从环境变量中获取 API 密钥

# 初始化 SQLite 数据库
DATABASE = 'articles.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                generated_content TEXT NOT NULL
            )
        ''')
        conn.commit()

# 首页：上传文章和查看生成结果
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            # 调用 OpenAI GPT-3 生成文章
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=user_input,
                max_tokens=500
            )
            generated_content = response.choices[0].text.strip()

            # 将用户输入和生成的文章保存到数据库
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO articles (user_input, generated_content)
                    VALUES (?, ?)
                ''', (user_input, generated_content))
                conn.commit()

            return redirect(url_for('index'))

    # 从数据库中获取所有文章记录
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles')
        articles = cursor.fetchall()

    return render_template('index.html', articles=articles)

# 删除文章
@app.route('/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
        conn.commit()
    return redirect(url_for('index'))

# 前端模板
@app.route('/template')
def template():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Article Generator</title>
    </head>
    <body>
        <h1>AI Article Generator</h1>
        <form method="POST" action="/">
            <textarea name="user_input" rows="10" cols="50" placeholder="Enter your text or topic here..."></textarea><br><br>
            <button type="submit">Generate Article</button>
        </form>

        <h2>Generated Articles</h2>
        <ul>
            {% for article in articles %}
                <li>
                    <strong>Input:</strong> {{ article[1] }}<br>
                    <strong>Generated Content:</strong> {{ article[2] }}<br>
                    <form method="POST" action="/delete/{{ article[0] }}" style="display:inline;">
                        <button type="submit">Delete</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
    </body>
    </html>
    '''

# 初始化数据库
init_db()

# 运行应用
if __name__ == '__main__':
    app.run(debug=True)