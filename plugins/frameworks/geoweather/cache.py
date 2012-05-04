"""
This module implements cache for HAL's geoweather framework
"""

try:
    import sqlite3
except ImportError:
    dummy = True
    def get(key, type):
        return None
    def set(key, value, type):
        return 0
else:
    dummy = False
    import os.path
    import atexit
    db_file = os.path.join(os.path.dirname(__file__), 'permanent.cache')
    db = sqlite3.connect(db_file, check_same_thread=False)
    db2 = sqlite3.connect(':memory:', check_same_thread=False)
    with db:
        db.execute('CREATE TABLE IF NOT EXISTS cache (key VARCHAR(32), value TEXT, type VARCHAR(22))')
    with db2:
        db2.execute('CREATE TABLE IF NOT EXISTS cache (key VARCHAR(32), value TEXT, type VARCHAR(22))')
    
    def get(key, type, temp=True):
        data = db2 if temp else db
        c = data.execute('SELECT * FROM cache WHERE key=? AND type=?', (key, type))
        try:
            return c.fetchone()[1]
        except TypeError:
            return None
    
    def set(key, value, type, temp=True):
        data = db2 if temp else db
        with data:
            c = data.execute('DELETE FROM cache WHERE key=? AND type=?', (key, type))
            c.execute('INSERT INTO cache VALUES (?, ?, ?)', (key, value, type))
            return c.rowcount
    
    def perma_get(*args, **kwargs):
        return get(*args, temp=False, **kwargs)
        
    def perma_set(*args, **kwargs):
        return set(*args, temp=False, **kwargs)
    
    @atexit.register
    def _cleanup():
        db.commit()

if __name__ == '__main__':
    if dummy:
        print 'You need sqlite3 to use this...'
        raise SystemExit
    while True:
        print eval(raw_input('>>> '))
