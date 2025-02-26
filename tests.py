import sys
import os

# Forçar uso da nova versão
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Configuração extra
os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'
os.environ['CHROMA_DB_IMPL'] = 'duckdb+parquet'

# Verificação
import sqlite3
print(f"✅ Versão SQLite: {sqlite3.sqlite_version}")  # Deve mostrar 3.45.1
