from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def init_db():
    print(f"Using database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            time_duration INTEGER NOT NULL,
            coin INTEGER NOT NULL,
            exp INTEGER NOT NULL,
            status INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lvl INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            coin INTEGER DEFAULT 0
        )
    ''')
    # Initialize user stats if not exists
    c.execute('SELECT count(*) FROM user_stats')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO user_stats (lvl, exp, coin) VALUES (1, 0, 0)')
    
    conn.commit()
    conn.close()

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/')
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Fetch user stats
    c.execute('SELECT * FROM user_stats WHERE id = 1')
    user = c.fetchone()
    
    # Fetch active quests (status = 1)
    c.execute('SELECT * FROM quests WHERE status = 1')
    active_quests = c.fetchall()
    
    conn.close()
    
    if not user:
        # Fallback if no user exists (though init_db creates one)
        user = {'lvl': 1, 'exp': 0, 'coin': 0}
        
    return render_template("main.html", user=user, active_quests=active_quests)

@app.route('/quest')
def quest():
    return render_template("quest_preview.html")

@app.route('/questlist')
def questlist():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM quests')
    quests = c.fetchall()
    
    # Also fetch user stats to display if needed (optional)
    # c.execute('SELECT * FROM user_stats WHERE id = 1')
    # user = c.fetchone()
    
    conn.close()
    return render_template("quest-main.html", quests=quests)

@app.route('/market')
def market():
    return render_template("market.html")

@app.route('/park')
def park():
    return render_template("park.html")

@app.route('/add_quest', methods=['POST'])
def add_quest():
    data = request.json
    quest_name = data.get('quest')
    difficulty = data.get('difficulty')
    time_duration = data.get('time')

    if not quest_name or not difficulty or not time_duration:
        return jsonify({'error': 'Missing data'}), 400

    # Calculate rewards
    rewards = {
        'easy': {'coin': 5, 'exp': 7},
        'normal': {'coin': 10, 'exp': 15},
        'hard': {'coin': 15, 'exp': 25}
    }
    
    reward = rewards.get(difficulty.lower(), {'coin': 0, 'exp': 0})
    coin = reward['coin']
    exp = reward['exp']

    exp = reward['exp']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO quests (quest_name, difficulty, time_duration, coin, exp, status) VALUES (?, ?, ?, ?, ?, 0)',
              (quest_name, difficulty, time_duration, coin, exp))
    conn.commit()
    conn.close()

    return jsonify({'message': '퀘스트가 성공적으로 등록되었습니다!', 'coin': coin, 'exp': exp}), 201

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    quest_id = data.get('id')
    new_status = data.get('status')

    if quest_id is None or new_status is None:
        return jsonify({'error': 'Missing data'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE quests SET status = ? WHERE id = ?', (new_status, quest_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Status updated successfully'}), 200

@app.route('/delete_quest', methods=['POST'])
def delete_quest():
    data = request.json
    quest_id = data.get('id')

    if quest_id is None:
        return jsonify({'error': 'Missing data'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Get quest rewards
    c.execute('SELECT coin, exp FROM quests WHERE id = ?', (quest_id,))
    quest = c.fetchone()
    
    if quest:
        coin_reward = quest[0]
        exp_reward = quest[1]
        
        # 2. Add to user stats (assuming user id 1)
        c.execute('UPDATE user_stats SET coin = coin + ?, exp = exp + ? WHERE id = 1', (coin_reward, exp_reward))
        
        # 3. Delete the quest
        c.execute('DELETE FROM quests WHERE id = ?', (quest_id,))
        conn.commit()
        msg = f'퀘스트가 완료되었습니다! {coin_reward} 코인과 {exp_reward} 경험치를 획득했습니다.'
    else:
        msg = '퀘스트를 찾을 수 없습니다.'

    conn.close()

    return jsonify({'message': msg}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
