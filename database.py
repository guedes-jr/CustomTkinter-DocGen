import sqlite3
import os
import json
import shutil
from datetime import datetime

DB_PATH = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Modelos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            cache_data TEXT
        )
    ''')
    
    # Metadados de Variáveis (Tooltips/Descrições)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variable_metadata (
            variable_name TEXT PRIMARY KEY,
            description TEXT
        )
    ''')
    
    # Biblioteca de Imagens (Assinaturas/Logos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL
        )
    ''')
    
    # Configurações do App (Tema, etc)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Admin padrão
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))

    # Tema padrão (Dark)
    cursor.execute('SELECT * FROM app_settings WHERE key = ?', ('theme',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO app_settings (key, value) VALUES (?, ?)', ('theme', 'dark'))
        
    conn.commit()
    conn.close()

# --- App Settings ---
def get_setting(key, default=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def save_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# --- Variable Metadata ---
def save_var_desc(var_name, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO variable_metadata (variable_name, description) VALUES (?, ?)', (var_name, description))
    conn.commit()
    conn.close()

def get_var_desc(var_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT description FROM variable_metadata WHERE variable_name = ?', (var_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

# --- Image Library ---
def add_library_image(name, path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO image_library (name, path) VALUES (?, ?)', (name, path))
    conn.commit()
    conn.close()

def get_library_images():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, path FROM image_library')
    images = cursor.fetchall()
    conn.close()
    return images

def delete_library_image(img_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM image_library WHERE id = ?', (img_id,))
    conn.commit()
    conn.close()

# --- Backup ---
def perform_backup(dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_docgen_{timestamp}.zip"
    backup_path = os.path.join(dest_folder, backup_name)
    
    # Criar pasta temporaria de backup
    temp_dir = "temp_backup"
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    if os.path.exists(DB_PATH): shutil.copy(DB_PATH, temp_dir)
    if os.path.exists('assets'): shutil.copytree('assets', os.path.join(temp_dir, 'assets'))
    
    shutil.make_archive(backup_path.replace('.zip', ''), 'zip', temp_dir)
    shutil.rmtree(temp_dir)
    return backup_path

# --- Existing Functions (Updated) ---
def check_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def add_new_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def update_user_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
    conn.commit()
    conn.close()

def add_template(name, path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO templates (name, path) VALUES (?, ?)', (name, path))
    conn.commit()
    conn.close()

def get_templates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, path FROM templates')
    templates = cursor.fetchall()
    conn.close()
    return templates

def get_template_cache(template_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT cache_data FROM templates WHERE id = ?', (template_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return {}
    return {}

def save_template_cache(template_id, cache_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    json_data = json.dumps(cache_dict)
    cursor.execute('UPDATE templates SET cache_data = ? WHERE id = ?', (json_data, template_id))
    conn.commit()
    conn.close()
