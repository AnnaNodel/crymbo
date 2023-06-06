import pytz
import pymongo
from pymongo import errors
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions

# from .config import config
# from wcommon.logger import log


class MongoClient:

    def __init__(self, collection, uri, database="wallter"):
        """
          Mongo Client
        :param  collection:  The collection to be used
        :param  database:  The database to be used
        :param  conf_section:  section in configuration file
        :param  max_pool: The maximum open connection
        :param  min_pool: The minimum open connection
        """
        #conf = config[conf_section]
        # DEF_URI = mongo_uri = "mongodb://Wallter:Wallter2020@13.41.160.110:27017"
        DEF_URI = mongo_uri = uri
        self.myclient = pymongo.MongoClient(mongo_uri)
        self.mydb = self.myclient[database]
        self.mycol = self.mydb[collection]

    def get_by(self, key, val):
        """
        Get by key and val
        :param key: key in object iban
        :param val: wanted value
        :return: dict if found, false if not
        """
        try:
            query = {key: {"$eq": val}}
            result = self.mycol.find_one(query)
            if result:
                result['_id'] = str(result['_id'])
            return result
        except pymongo.errors.PyMongoError as e:
            #log.exception(str(e))
            return None
        except Exception as e:
            #log.exception(str(e))
            return None