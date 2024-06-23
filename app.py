from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from transformers import pipeline
from langdetect import detect
import math

app = Flask(__name__)
app.secret_key = 'idk'
login_manager = LoginManager()
login_manager.init_app(app)

# In-memory user storage
users = {'user@example.com': {'password': 'password', 'summaries': []}}

# Dummy user class
class User(UserMixin):
    def __init__(self, email):
        self.id = email

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Load pre-trained model
summarizer = pipeline('summarization')

def summarize_text(text, lang='en'):
    if lang != 'en':
        # Load language-specific summarization model if available
        summarizer = pipeline('summarization', model=f'{lang}_summarization_model')
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            user = User(email)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/summarize', methods=['POST'])
@login_required
def summarize():
    text = request.form['text']
    if not text:
        flash('No text provided!')
        return redirect(url_for('home'))
    lang = detect(text)
    summary = summarize_text(text, lang)
    users[current_user.id]['summaries'].append({'original': text, 'summary': summary})
    return render_template('result.html', summary=summary, original_text=text)

@app.route('/summaries')
@login_required
def summaries():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    summaries = users[current_user.id]['summaries']
    total = len(summaries)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_summaries = summaries[start:end]
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': math.ceil(total / per_page)
    }
    return render_template('summaries.html', summaries=paginated_summaries, pagination=pagination)

if __name__ == '__main__':
    app.run(debug=True)

