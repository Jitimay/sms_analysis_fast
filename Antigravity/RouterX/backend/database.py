import sqlite3
import json
from datetime import datetime
import uuid

class Database:
    def __init__(self, db_path="routex.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_address TEXT,
                amount REAL,
                route_id TEXT,
                route_name TEXT,
                fee REAL,
                savings REAL,
                status TEXT,
                tx_hash TEXT,
                destination TEXT,
                created_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_transaction(self, tx_data):
        conn = sqlite3.connect(self.db_path)
        tx_id = str(uuid.uuid4())
        conn.execute('''
            INSERT INTO transactions (id, user_address, amount, route_id, route_name, fee, savings, status, destination, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tx_id, tx_data['user_address'], tx_data['amount'], tx_data['route_id'], 
              tx_data['route_name'], tx_data['fee'], tx_data['savings'], 'pending', 
              tx_data['destination'], datetime.now()))
        conn.commit()
        conn.close()
        return tx_id
    
    def update_transaction(self, tx_id, status, tx_hash=None):
        conn = sqlite3.connect(self.db_path)
        if tx_hash:
            conn.execute('''
                UPDATE transactions SET status=?, tx_hash=?, completed_at=?
                WHERE id=?
            ''', (status, tx_hash, datetime.now(), tx_id))
        else:
            conn.execute('UPDATE transactions SET status=? WHERE id=?', (status, tx_id))
        conn.commit()
        conn.close()
    
    def get_user_transactions(self, user_address):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT id, amount, destination, route_name, fee, savings, status, created_at, tx_hash
            FROM transactions WHERE user_address=? ORDER BY created_at DESC LIMIT 20
        ''', (user_address,))
        transactions = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'amount', 'destination', 'route', 'fee', 'savings', 'status', 'date', 'txHash'], tx)) for tx in transactions]
