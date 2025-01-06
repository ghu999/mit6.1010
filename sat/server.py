#!/usr/bin/env python3
import os
import sys
import json
import time
import pickle
import importlib
import mimetypes
import traceback

from wsgiref.handlers import read_environ
from wsgiref.simple_server import make_server

import lab

LAB_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(LAB_DIR, "test_inputs")


def load_json(fname):
    with open(os.path.join(TEST_DIR, fname), "r") as f:
        return (fname.removesuffix(".json"), json.load(f))


tests = filter(
    lambda x: isinstance(x[1][0], dict),
    map(load_json, filter(lambda x: x.endswith("json"), os.listdir(TEST_DIR))),
)

tests = dict(tests)


def trim(val, lim=400):
    s = str(val)
    return s[:lim] + ("..." if len(s) > lim else "")


def ui_assign(params):
    case = params["case"]
    try:
        sat = lab.boolify_scheduling_problem(
            {k: set(v) for k, v in case[0].items()}, case[1]
        )
        print("lab.boolify_scheduling_problem returned: " + trim(sat), flush=True)
        assign = lab.satisfying_assignment(sat)
        print("lab.satisfying_assignment returned: " + trim(assign), flush=True)
        return assign
    except:
        print(traceback.format_exc(), flush=True)
        return {}


funcs = {
    "/load_data": lambda p: [sorted(tests), tests],
    "/ui_assign": ui_assign,
}


def parse_post(environ):
    try:
        body_size = int(environ.get("CONTENT_LENGTH", 0))
    except:
        body_size = 0

    body = environ["wsgi.input"].read(body_size)
    try:
        return json.loads(body)
    except:
        return {}


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/") or "/"
    params = parse_post(environ)
    if path in funcs:
        status = "200 OK"
        type_ = "application/json"
        try:
            result = funcs[path](params)
        except Exception as e:
            print(str(e))
            result = {}
        body = json.dumps(result).encode("utf-8")
    else:
        if path == "/":
            static_file = "/ui/index.html"
        else:
            static_file = path

        static_file = static_file.lstrip("/")

        if static_file.startswith("ui/"):
            static_file = static_file[3:]

        static_fname = os.path.join(os.path.dirname(__file__), "ui", static_file)

        try:
            status = "200 OK"
            with open(static_fname, "rb") as f:
                body = f.read()
            type_ = mimetypes.guess_type(static_fname)[0] or "text/plain"
        except FileNotFoundError:
            status = "404 FILE NOT FOUND"
            body = static_fname.encode("utf-8")
            type_ = "text/plain"

    len_ = str(len(body))
    headers = [("Content-type", type_), ("Content-length", len_)]
    start_response(status, headers)
    return [body]


if __name__ == "__main__":
    PORT = 6101
    print(f"starting server.  navigate to http://localhost:{PORT}/")
    with make_server("", PORT, application) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down.")
            httpd.server_close()
