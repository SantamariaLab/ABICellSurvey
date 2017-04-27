# http://stackoverflow.com/questions/17053435/mysql-connector-python-insert-python-variable-to-mysql-table
#import mysql.connector.conversion.MySQLConverter
from mysql.connector.conversion import MySQLConverter

class NumpyMySQLConverter(MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """
        
    def __init__(self, charset=None, use_unicode=True):
        MySQLConverter.__init__(self, charset, use_unicode)
        self._cache_field_types = {}

    def _float32_to_mysql(self, value):
#         print "_float32_to_mysql:", value 
        return float(value)

    def _float64_to_mysql(self, value):
#         print "_float64_to_mysql:", value 
        return float(value)

    def _int32_to_mysql(self, value):
#         print "_int32_to_mysql:", value 
        return int(value)

    def _int64_to_mysql(self, value):
#         print "_int64_to_mysql:", value 
        return int(value)
