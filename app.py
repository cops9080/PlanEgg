from flask import Flask, render_template, request, jsonify, redirect, url_for
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

@app.route('/')
def main():
    return render_template("login.html")

@app.route('/home')
def home():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # User 정보 가져오기
    c.execute('SELECT * FROM user_stats WHERE id = 1')
    user = c.fetchone()
    
    # 활성화된 퀘스트 가져오기
    c.execute('SELECT * FROM quests WHERE status = 1')
    active_quests = c.fetchall()
    
    conn.close()
    
    if not user:
        user = {'lvl': 1, 'exp': 0, 'coin': 0}
        
    # 데이터를 가지고 main.html을 렌더링
    return render_template("main.html", user=user, active_quests=active_quests)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 여기에 아이디/비밀번호 확인하는 코드를 추가할 예정 
        return redirect(url_for('streak'))

    return render_template("login.html")

@app.route('/streak')
def streak():
    return render_template("streak.html")

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
    print("Park route accessed")
    return render_template("park.html")

@app.route('/user/<name>')
def user(name):
    friends_data = {
        '멍이': {
            'name': '멍이',
            'status': '📝 공부 중이에요!',
            'image': 'images/park/dreamina-2025-11-08-8642-Using image 1 as a reference, change the...-Photoroom 1.png',
            'quest': '토익 공부하기',
            'quest_time': '1:05',
            'quest_exp': 15
        },
        '냥이': {
            'name': '냥이',
            'status': 'chill한 기분이에요',
            'image': 'images/park/image 1.png',
            'quest': '낮잠 자기',
            'quest_time': '2:00',
            'quest_exp': 10
        },
        '포포': {
            'name': '포포',
            'status': '아무 생각이 없어요',
            'image': 'images/park/dreamina-2025-11-05-3975-Edit Image 1, remove the hat, and change...-Photoroom 1.png',
            'quest': '휴식 중',
            'quest_time': '-',
            'quest_exp': 0,
            'quest_difficulty': '-'
        }
    }
    
    if name == '포포':
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Fetch the most recent active quest
        c.execute('SELECT * FROM quests WHERE status = 1 ORDER BY id DESC LIMIT 1')
        active_quest = c.fetchone()
        conn.close()
        
        if active_quest:
            friends_data['포포']['quest'] = active_quest['quest_name']
            # Format time (assuming time_duration is in minutes)
            friends_data['포포']['quest_time'] = f"{active_quest['time_duration']}분"
            friends_data['포포']['quest_exp'] = active_quest['exp']
            friends_data['포포']['quest_difficulty'] = active_quest['difficulty']
    
    friend = friends_data.get(name)
    if not friend:
        # Default fallback if name not found
        friend = friends_data['멍이']
        
    return render_template("friend_detail.html", friend=friend)

@app.route('/ranking')
def ranking():
    # Fetch real user stats
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM user_stats WHERE id = 1')
    user = c.fetchone()
    conn.close()

    if not user:
        user = {'lvl': 1, 'exp': 0}

    # Mock data for ranking
    rankers = [
        {
            'name': '멍이',
            'lvl': 5,
            'exp': 350,
            'image': url_for('static', filename='images/park/dreamina-2025-11-08-8642-Using image 1 as a reference, change the...-Photoroom 1.png')
        },
        {
            'name': '냥이',
            'lvl': 4,
            'exp': 300,
            'image': url_for('static', filename='images/park/image 1.png')
        },
        {
            'name': '포포',
            'lvl': user['lvl'],
            'exp': user['exp'],
            'image': url_for('static', filename='images/park/dreamina-2025-11-05-3975-Edit Image 1, remove the hat, and change...-Photoroom 1.png')
        }
    ]
    
    # Sort rankers by exp descending
    rankers.sort(key=lambda x: x['exp'], reverse=True)
    
    return render_template("ranking.html", rankers=rankers)

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
        
        # Check for level up
        c.execute('SELECT lvl, exp FROM user_stats WHERE id = 1')
        row = c.fetchone()
        current_lvl = row[0]
        current_exp = row[1]
        
        leveled_up = False
        while current_exp >= 100:
            current_lvl += 1
            current_exp -= 100
            leveled_up = True
            
        if leveled_up:
            c.execute('UPDATE user_stats SET lvl = ?, exp = ? WHERE id = 1', (current_lvl, current_exp))
        
        # 3. Delete the quest
        c.execute('DELETE FROM quests WHERE id = ?', (quest_id,))
        conn.commit()
        
        if leveled_up:
            msg = f'퀘스트 완료! {coin_reward} 코인, {exp_reward} 경험치 획득. 레벨업! Lv.{current_lvl} 달성!'
        else:
            msg = f'퀘스트가 완료되었습니다! {coin_reward} 코인과 {exp_reward} 경험치를 획득했습니다.'
    else:
        msg = '퀘스트를 찾을 수 없습니다.'

    conn.close()



    return jsonify({'message': msg}), 200

@app.route('/room', methods=['GET'])
def room():
    return render_template('room.html')

@app.route('/reset_db', methods=['POST'])
def reset_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Reset user stats
    c.execute('UPDATE user_stats SET lvl = 1, exp = 0, coin = 0 WHERE id = 1')
    
    # Delete all quests
    c.execute('DELETE FROM quests')
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '데이터가 초기화되었습니다.'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
