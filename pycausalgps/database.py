"""
database.py
=======================================
The core module for the Database class.
"""

from linecache import cache
from sqlitedict import SqliteDict
from collections import OrderedDict
from itertools import islice

from .log import LOGGER


class Database:
    """ Database class"""

    _instance = None

    def __new__(cls, dbname):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, dbname):

            self.name = f'{dbname}'
            self.cache_size = 1000
            self.cache = OrderedDict()

    def __str__(self):
        return f"SQLitedict Database: {self.name}"

    def __repr__(self):
        return f"Database({self.name},{self.cache_size})"

    def set_value(self, key, value):
        """ 
        Sets the key and given value in the database. If the key exists,
        it will override the value. In that case, it will remove the key from
        the in-memory dictionary. It will be loaded again with the get_value
        command if needed.
        Inputs:
            | key: hash value (generated by the package)
            | value: Seismic Record object
        """
        try:
            db = SqliteDict(self.name, autocommit=True)
            db[key] = value
            del self.cache[key]
            db.commit()
            db.close()
        except KeyError:
            LOGGER.debug(f"Tried to delete non-existing {key} on the cache.")
        except Exception:
            LOGGER.warning(f"Tried to set {key} on the database."
             "Something went wrong.")
        finally:
            pass 

    def delete_value(self,key):
        """ Deletes the key, and its value from both in-memory dictionary and
        on-disk database. If the key is not found, simply ignores it.
        Inputs:
            | key: hash value (generated by the package)
        """
        try:
            db = SqliteDict(self.name, autocommit=True)
            del db[key]   
            try: 
                del self.cache[key]
            except:
                pass         
            LOGGER.debug(f"Value {key} is removed from database.")
            db.commit()
            db.close()
        except KeyError:
            LOGGER.warning(f"Tried to delete {key} on the database."
             "Something went wrong.")

    def get_value(self, key):
        """ Returns the value in the following order:
        
        | 1) It will look for the value in the cache and return it, if not found
        | 2) will look for the value in the disk and return it, if not found
        | 3) will return None.
        Inputs:
            | key: hash value (generated by the package)
        Outputs:
            | If found, value, else returns None.         
        """
        value = None
        try:
            value = self.cache[key]
            LOGGER.debug(f"Key: {key}. Value is loaded from the cache.")
        except:
            LOGGER.debug(f"Key: {key}. Value is not found in the cache.")

        if not value:
            try:
                db = SqliteDict(self.name, autocommit=True)
                tmp = db[key]
                if len(self.cache) >  self.cache_size:
                    self.cache.popitem(last=False)
                    LOGGER.debug(f"cache size is more than limit"
                     f"{self.cache_size}. An item removed, and new item added.")
                self.cache[key] = tmp
                return tmp
            except Exception:
                LOGGER.debug(f"The requested key ({key}) is not in the"
                 " database. Returns None.")
                return None
            finally:
                db.commit()
                db.close()
        else:
            return value

    def cache_summary(self):
        print(f"Current cache size: {self.cache_size}")

    def update_cache_size(self, new_size):
        self.cache_size = new_size
        if self.cache_size > new_size:
            keys = list(islice(self.cache, new_size))
            tmp_cache = OrderedDict()
            for key in keys:
                tmp_cache[key] = self.cache[key]
            self.cache = tmp_cache

    def close_db(self):
        """ Commits changes to the database, closes the database, clears the 
        cache.
        """

        self.cache = None
        LOGGER.info(f"Database ({self.name}) is closed.")