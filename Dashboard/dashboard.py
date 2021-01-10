from datetime import date, datetime
import http.server
from socketserver import TCPServer
import redis
from os import getenv
import json
from dotenv import load_dotenv

global r
if getenv("is_docker") == "true":
    r = redis.Redis(host = "redis", port = 6379)
else:
    load_dotenv("../.env")
    r = redis.Redis(db = getenv("redis_db_index"), password = getenv("redis_key"))

def generate_csv_pulse() -> str:
    keys = r.lrange("HP_consumption", 0, -1)
    parsed = []
    for key in keys:
        parsed.append(json.loads(key))
    csv: str = ""
    for key in parsed:
        csv += datetime.fromisoformat(key["datetime"]).date().isoformat()
        csv += ";"
        csv += datetime.fromisoformat(key["datetime"]).time().isoformat()
        csv += ";"
        csv += str(key["energy"])
        csv += ";"
        csv += str(key["power"])
        csv += ";"
        csv += str(key["restart"])
        csv += "\n"
    return csv

def generate_csv_daily() -> str:
    keys = r.lrange("HP_consumption_daily", 0, -1)
    parsed = []
    for key in keys:
        parsed.append(json.loads(key))
    csv: str = ""
    for key in parsed:
        csv += date.fromisoformat(key["date"]).isoformat()
        csv += ";"
        csv += str(key["energy"])
        csv += ";"
        csv += str(key["restart"])
        csv += "\n"
    return csv

def send_csv(self: http.server.SimpleHTTPRequestHandler, csv: str, filename: str):
    self.send_response(200)

    self.send_header("Content-Type", "text/csv")
    self.send_header("Content-Disposition", "inline; filename=\"" + filename + ".csv\"")
    self.end_headers()

    self.wfile.write(bytes(csv, "utf8"))

class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/pulse':
            send_csv(self, generate_csv_pulse(), datetime.now().isoformat() + "_pulse")
        else:
            send_csv(self, generate_csv_daily(), datetime.now().isoformat() + "_daily")
        
        return

with TCPServer(("", 80), HttpRequestHandler) as httpd:
    print("Server is running at port 80")
    httpd.serve_forever()