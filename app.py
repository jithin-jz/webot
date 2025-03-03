from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from instagrapi import Client
import time
import random
from colorama import Fore, Back, Style, init
import threading
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Store bot instances
bots = {}

# Initialize colorama
init(autoreset=True)

class InstagramBot:
    def __init__(self, username, password):
        self.client = Client()
        self.username = username
        self.password = password
        self.action_count = 0
        self.is_running = False
        self.current_task = None
        self.task_thread = None
        self.login()

    def login(self):
        """Log in to Instagram."""
        try:
            self.client.login(self.username, self.password)
            return True, f"Logged in as {self.username}"
        except Exception as e:
            return False, f"Login failed: {str(e)}"

    def logout(self):
        """Log out of Instagram."""
        try:
            self.client.logout()
            return True, "Logged out successfully"
        except:
            return False, "Logout failed"

    def _random_delay(self, min_sec=10, max_sec=30):
        """Add a random delay between actions."""
        delay = random.randint(min_sec, max_sec)
        time.sleep(delay)

    def _increment_action_count(self):
        """Increment the action counter."""
        self.action_count += 1

    def like_posts_by_hashtag(self, hashtag, count=5):
        """Like posts from a specific hashtag."""
        self.is_running = True
        results = []
        try:
            posts = self.client.hashtag_medias_recent(hashtag, amount=count)
            for post in posts:
                if not self.is_running:
                    break
                if self.action_count >= 300:
                    results.append("Daily like limit reached")
                    break
                self.client.media_like(post.id)
                results.append(f"Liked post: {post.code}")
                self._increment_action_count()
                self._random_delay()
        except Exception as e:
            results.append(f"Error: {str(e)}")
        self.is_running = False
        return results

    def follow_followers_of_account(self, target_user, limit=5):
        """Follow followers of a specific account."""
        self.is_running = True
        results = []
        try:
            user_id = self.client.user_id_from_username(target_user)
            followers = self.client.user_followers(user_id, amount=limit)
            for user in followers.values():
                if not self.is_running:
                    break
                if self.action_count >= 100:
                    results.append("Daily follow limit reached")
                    break
                try:
                    self.client.user_follow(user.pk)
                    results.append(f"Followed {user.username}")
                    self._increment_action_count()
                    self._random_delay()
                except Exception as e:
                    results.append(f"Error following {user.username}: {str(e)}")
        except Exception as e:
            results.append(f"Error: {str(e)}")
        self.is_running = False
        return results

    def unfollow_non_followers(self):
        """Unfollow users who don't follow back."""
        self.is_running = True
        results = []
        try:
            following = self.client.user_following(self.client.user_id)
            followers = self.client.user_followers(self.client.user_id)
            
            following_ids = set(following.keys())
            followers_ids = set(followers.keys())
            non_followers = following_ids - followers_ids

            for user_id in list(non_followers)[:10]:
                if not self.is_running:
                    break
                if self.action_count >= 100:
                    results.append("Daily unfollow limit reached")
                    break
                self.client.user_unfollow(user_id)
                username = following[user_id].username
                results.append(f"Unfollowed {username}")
                self._increment_action_count()
                self._random_delay()
        except Exception as e:
            results.append(f"Error: {str(e)}")
        self.is_running = False
        return results

    def comment_on_latest_posts(self, comment="Great post! 👏"):
        """Like + comment on latest posts of followed accounts."""
        self.is_running = True
        results = []
        try:
            following = self.client.user_following(self.client.user_id)
            for user in following.values():
                if not self.is_running:
                    break
                if self.action_count >= 50:
                    results.append("Daily comment limit reached")
                    break
                try:
                    posts = self.client.user_medias(user.pk, amount=1)
                    if posts:
                        post = posts[0]
                        self.client.media_like(post.pk)
                        self.client.media_comment(post.pk, comment)
                        results.append(f"Liked and commented on {user.username}'s post")
                        self._increment_action_count()
                        self._random_delay()
                except Exception as e:
                    results.append(f"Error: {str(e)}")
        except Exception as e:
            results.append(f"Error: {str(e)}")
        self.is_running = False
        return results

    def view_stories(self):
        """View stories of all followed accounts."""
        self.is_running = True
        results = []
        try:
            following = self.client.user_following(self.client.user_id)
            for user in following.values():
                if not self.is_running:
                    break
                try:
                    stories = self.client.user_stories(user.pk)
                    if stories:
                        story_pks = [s.pk for s in stories]
                        self.client.story_seen(story_pks)
                        results.append(f"Viewed {len(story_pks)} stories by {user.username}")
                        self._random_delay()
                except Exception as e:
                    results.append(f"Error: {str(e)}")
        except Exception as e:
            results.append(f"Error: {str(e)}")
        self.is_running = False
        return results

    def dm_new_followers(self, message="Thanks for following!"):
        """DM new followers."""
        self.is_running = True
        results = []
        try:
            followers = self.client.user_followers(self.client.user_id)
            for user in followers.values():
                if not self.is_running:
                    break
                if self.action_count >= 50:
                    results.append("Daily DM limit reached")
                    break
                self.client.direct_send(message, user_ids=[user.pk])
                results.append(f"DM sent to {user.username}")
                self._increment_action_count()
                self._random_delay()
        except Exception as e:
            results.append(f"Error: {str(e)}")
        self.is_running = False
        return results

    def is_following_user(self, target_user):
        """Check if following a user."""
        try:
            user_id = self.client.user_id_from_username(target_user)
            return user_id in self.client.user_following(self.client.user_id)
        except Exception as e:
            return False

    def stop_current_task(self):
        """Stop the current running task."""
        self.is_running = False
        if self.task_thread and self.task_thread.is_alive():
            self.task_thread.join()
        self.current_task = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_bot():
    """Get the bot instance for the current user."""
    username = session.get('username')
    return bots.get(username)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in bots:
        # Reuse existing bot if it exists
        bot = bots[username]
    else:
        # Create new bot instance
        bot = InstagramBot(username, password)
        success, message = bot.login()
        if not success:
            return render_template('login.html', error=message)
        bots[username] = bot
    
    session['username'] = username
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    bot = get_bot()
    if not bot:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=bot.username, action_count=bot.action_count)

@app.route('/api/like_hashtag', methods=['POST'])
@login_required
def like_hashtag():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    hashtag = request.form.get('hashtag', '').strip('#')
    count = int(request.form.get('count', 5))
    
    def run_task():
        bot.current_task = bot.like_posts_by_hashtag(hashtag, count)
    
    bot.task_thread = threading.Thread(target=run_task)
    bot.task_thread.start()
    return jsonify({"status": "started"})

@app.route('/api/follow_followers', methods=['POST'])
@login_required
def follow_followers():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    target = request.form.get('target')
    limit = int(request.form.get('limit', 5))
    
    def run_task():
        bot.current_task = bot.follow_followers_of_account(target, limit)
    
    bot.task_thread = threading.Thread(target=run_task)
    bot.task_thread.start()
    return jsonify({"status": "started"})

@app.route('/api/unfollow_non_followers', methods=['POST'])
@login_required
def unfollow_non_followers():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    def run_task():
        bot.current_task = bot.unfollow_non_followers()
    
    bot.task_thread = threading.Thread(target=run_task)
    bot.task_thread.start()
    return jsonify({"status": "started"})

@app.route('/api/comment_posts', methods=['POST'])
@login_required
def comment_posts():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    comment = request.form.get('comment', 'Great post! 👏')
    
    def run_task():
        bot.current_task = bot.comment_on_latest_posts(comment)
    
    bot.task_thread = threading.Thread(target=run_task)
    bot.task_thread.start()
    return jsonify({"status": "started"})

@app.route('/api/view_stories', methods=['POST'])
@login_required
def view_stories():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    def run_task():
        bot.current_task = bot.view_stories()
    
    bot.task_thread = threading.Thread(target=run_task)
    bot.task_thread.start()
    return jsonify({"status": "started"})

@app.route('/api/dm_followers', methods=['POST'])
@login_required
def dm_followers():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    message = request.form.get('message', 'Thanks for following!')
    
    def run_task():
        bot.current_task = bot.dm_new_followers(message)
    
    bot.task_thread = threading.Thread(target=run_task)
    bot.task_thread.start()
    return jsonify({"status": "started"})

@app.route('/api/stop_task', methods=['POST'])
@login_required
def stop_task():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    bot.stop_current_task()
    return jsonify({"status": "stopped"})

@app.route('/api/task_status')
@login_required
def task_status():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Not logged in"}), 401
    
    if bot.current_task:
        return jsonify({
            "status": "running" if bot.is_running else "completed",
            "results": bot.current_task
        })
    return jsonify({"status": "no_task"})

@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        if username in bots:
            bot = bots[username]
            bot.logout()
            del bots[username]
        session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
