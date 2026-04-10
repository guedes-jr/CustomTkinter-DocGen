import sqlite3
import os
import json
import shutil
import socket
import fcntl
import struct
from datetime import datetime
import hashlib
import time

LOCK_FILE = 'database.lock'

def get_lock_name():
    hostname = socket.gethostname()
    return f"docgen_{hashlib.md5(hostname.encode()).hexdigest()[:8]}"

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_data = json.load(f)
                lock_name = lock_data.get('name', '')
                timestamp = lock_data.get('timestamp', 0)
                
                if lock_name != get_lock_name():
                    if time.time() - timestamp > 300:
                        os.remove(LOCK_FILE)
                    else:
                        return False, lock_data
        except:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
    
    lock_data = {
        'name': get_lock_name(),
        'timestamp': time.time(),
        'hostname': socket.gethostname()
    }
    with open(LOCK_FILE, 'w') as f:
        json.dump(lock_data, f)
    return True, lock_data

def release_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_data = json.load(f)
                if lock_data.get('name') == get_lock_name():
                    os.remove(LOCK_FILE)
        except:
            pass

def check_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_data = json.load(f)
                lock_name = lock_data.get('name', '')
                timestamp = lock_data.get('timestamp', 0)
                hostname = lock_data.get('hostname', '')
                
                if lock_name != get_lock_name():
                    if time.time() - timestamp > 300:
                        os.remove(LOCK_FILE)
                        return True
                    return False, hostname
        except:
            return True
    return True

def is_process_running():
    result = check_lock()
    if result is True:
        return True
    return result

def get_db_path():
    return DB_PATH

def get_lock_file():
    return os.path.join(os.path.dirname(DB_PATH), 'database.lock') if DB_PATH else 'database.lock'

def set_db_path(db_file_path):
    global DB_PATH, LOCK_FILE
    DB_PATH = db_file_path
    LOCK_FILE = get_lock_file()
    
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        conn.close()
    
    temp_conn = sqlite3.connect('database.db')
    temp_cursor = temp_conn.cursor()
    temp_cursor.execute('INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)', ('db_path', db_file_path))
    temp_conn.commit()
    temp_conn.close()
    
    if on_db_change_callback:
        on_db_change_callback()

on_db_change_callback = None

def set_on_db_change(callback):
    global on_db_change_callback
    on_db_change_callback = callback

DB_PATH = 'database.db'
LOCK_FILE = 'database.lock'

def init_db():
    global DB_PATH, LOCK_FILE
    
    default_db = 'database.db'
    if not os.path.exists(default_db):
        conn = sqlite3.connect(default_db)
        conn.close()
    
    db_path = default_db
    if os.path.exists(default_db):
        try:
            conn = sqlite3.connect(default_db)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM app_settings WHERE key = ?', ('db_path',))
            row = cursor.fetchone()
            conn.close()
            if row:
                saved_path = row[0]
                saved_abs = os.path.abspath(saved_path)
                default_abs = os.path.abspath(default_db)
                if saved_abs == default_abs:
                    db_path = default_db
                elif os.path.isfile(saved_path):
                    db_path = saved_path
        except:
            pass
    
    DB_PATH = db_path
    LOCK_FILE = get_lock_file()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            group_name TEXT DEFAULT 'user'
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
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()
    release_write_operation()

# --- Variable Metadata ---
def save_var_desc(var_name, description):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO variable_metadata (variable_name, description) VALUES (?, ?)', (var_name, description))
    conn.commit()
    conn.close()
    release_write_operation()

def get_var_desc(var_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT description FROM variable_metadata WHERE variable_name = ?', (var_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

# --- Image Library ---
def add_library_image(name, path):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO image_library (name, path) VALUES (?, ?)', (name, path))
    conn.commit()
    conn.close()
    release_write_operation()

def get_library_images():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, path FROM image_library')
    images = cursor.fetchall()
    conn.close()
    return images

def delete_library_image(img_id):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM image_library WHERE id = ?', (img_id,))
    conn.commit()
    conn.close()
    release_write_operation()

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
    cursor.execute('SELECT id, username, group_name FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_group(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT group_name FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'user'

def add_new_user(username, password, group='user'):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, group_name) VALUES (?, ?, ?)', (username, password, group))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
        release_write_operation()

def delete_user(user_id):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    release_write_operation()

def update_user_password(user_id, new_password):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
    conn.commit()
    conn.close()
    release_write_operation()

def add_template(name, path):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO templates (name, path) VALUES (?, ?)', (name, path))
    conn.commit()
    conn.close()
    release_write_operation()

def delete_template(template_id):
    valid, error = validate_write_operation()
    if not valid:
        raise Exception(error)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM templates WHERE id = ?', (template_id,))
    row = cursor.fetchone()
    if row and os.path.exists(row[0]):
        try:
            os.remove(row[0])
        except:
            pass
    cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()
    release_write_operation()

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
    if not is_process_running():
        raise Exception("Outro processo está usando o banco de dados. Aguarde ou verifique as conexões ativas.")
    
    success, _ = acquire_lock()
    if not success:
        raise Exception("Não foi possível adquirir lock. Outro processo pode estar alterando o banco.")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        json_data = json.dumps(cache_dict)
        cursor.execute('UPDATE templates SET cache_data = ? WHERE id = ?', (json_data, template_id))
        conn.commit()
        conn.close()
    finally:
        release_lock()

def validate_write_operation():
    if not is_process_running():
        return False, "Outro processo está usando o banco de dados. Aguarde ou verifique as conexões ativas."
    
    success, lock_info = acquire_lock()
    if not success:
        return False, f"Banco bloqueado por: {lock_info.get('hostname', 'desconhecido')}"
    return True, None

def release_write_operation():
    release_lock()
