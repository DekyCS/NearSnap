import datetime
import pytz
from dateutil import parser


timestamp_str = datetime.datetime.now(pytz.timezone('US/Eastern'))
date_time_obj = parser.parse(timestamp_str)
time_passed = datetime.now() - date_time_obj  
print(time_passed)  

month = timestamp_str.strftime("%m")
year = timestamp_str.strftime("%Y")

print(f"Omar's version: {month}, {year}")






    

