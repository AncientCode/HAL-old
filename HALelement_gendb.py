import sqlite3

db = sqlite3.connect('data/element.db')
c = db.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS elements (z INTEGER PRIMARY KEY,
                                                  symbol VARCHAR(2),
                                                  name VARCHAR(20),
                                                  group_ INTEGER,
                                                  period INTEGER,
                                                  weight VARCHAR(20),
                                                  density VARCHAR(20),
                                                  melt VARCHAR(10),
                                                  boil VARCHAR(10),
                                                  heat VARCHAR(10),
                                                  electronegativity VARCHAR(10),
                                                  abundance VARCHAR(10));""")

with open('elementdata.txt') as file:
    for line in file:
        print line.strip()
        z, sym, name, group, period, weight, density, melt, boil, heat, neg, abundance = line.split()
        c.execute('INSERT INTO elements VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (z, sym, name, group, period, weight, density, melt, boil, heat, neg, abundance))

db.commit()
print 'Done generating database!'
