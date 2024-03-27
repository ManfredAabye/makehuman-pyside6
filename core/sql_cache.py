import sqlite3
import os

class FileCache:
    def __init__(self, name):
        print ("Initializing: " + name)
        self.con = sqlite3.connect(name)
        self.cur = self.con.cursor()
        self.name = name
        self.time = int(os.stat(name).st_mtime)
        print (self.time)

    def createCache(self, latest, subdir=None):
        res = self.cur.execute("SELECT name FROM sqlite_master WHERE name='filecache'")
        if res.fetchone() is None:
            print ("Need to create table")
            self.cur.execute("CREATE TABLE filecache(name, uuid, path, folder, obj_file, thumbfile, author, tags)")
            return(True)

        if subdir is None:
            if latest > self.time:
                print ("Need to cleanup file table")
                self.cur.execute("DELETE FROM filecache")
                return (True)
            else:
                return(False)
        else:
            print("DELETE FROM filecache where folder = " +  subdir)
            self.cur.execute("DELETE FROM filecache where folder = ?", (subdir,))
            self.con.commit()
            return (True)

    def listCache(self):
        rows = self.cur.execute("SELECT * FROM filecache ORDER BY name COLLATE NOCASE ASC")
        return(rows)

    def insertCache(self, data):
        self.cur.executemany("insert into filecache values(?, ?, ?, ?, ?, ?, ?, ?)", data)
        self.con.commit()
        self.time = int(os.stat(self.name).st_mtime)

    def __del__(self):
        self.cur.close()

