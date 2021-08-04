#!/usr/bin/python3

from datetime import datetime
import http.server
from socketserver import TCPServer
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

global mongo
global db
if getenv("is_docker") == "true":
    mongo = MongoClient(host="mongodb", username=getenv("MONGODB_ROOT_USERNAME"),
                        password=getenv("MONGODB_ROOT_PASSWORD"))
    db = mongo["energymeter"]
else:
    load_dotenv("../.env")
    mongo = MongoClient(host=getenv("MONGODB_HOST"), port=getenv("MONGODB_PORT", 27017),
                        username=getenv("MONGODB_ROOT_USERNAME"), password=getenv("MONGODB_ROOT_PASSWORD"))
    db = mongo[getenv("MONGODB_DATABASE_NAME", "energymeter")]


def generate_csv(key: str) -> str:
    collection = db[key]
    keys = collection.find()

    csv = ""
    for key in keys:
        d = datetime.fromisoformat(key["_id"])

        if "T" in key["_id"]:  # key is a pulse (date+time)
            csv += d.date().isoformat()
            csv += ";"
            csv += d.time().isoformat()
            csv += ";"
            csv += str(key["energy"])
            csv += ";"
            csv += str(key["power"])
            csv += ";"
        else:  # key is a day overview (date)
            csv += d.date().isoformat()
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
            send_csv(self, generate_csv("HP_consumption"), datetime.now().isoformat() + "_pulse")
        else:
            send_csv(self, generate_csv("HP_consumption_daily"), datetime.now().isoformat() + "_daily")
        return


with TCPServer(("", 80), HttpRequestHandler) as httpd:
    print("Server is running at port 80")
    httpd.serve_forever()