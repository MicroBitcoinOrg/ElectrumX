#!/usr/bin/env python3
"""
Usage::
    ./rpcd.py [<port>]
"""
from aiorpcx import ClientSession
from server.controller import Controller
from http.server import BaseHTTPRequestHandler, HTTPServer
from server.version import NAME
from urllib import parse
from os import environ
import asyncio
import json
import re

node_name = NAME
port = int(environ.get('RPC_PORT', 7403))
rpc_port = int(environ.get('RPC_PORT', 8000))
allowed = [
    'blockchain.address.allutxo',
    'blockchain.address.balance',
    'blockchain.address.history',
    'blockchain.address.mempool',
    'blockchain.address.utxo',
    'blockchain.address.pgutxo',
    'blockchain.address.info',
    'blockchain.block.info',
    'blockchain.block.range',
    'blockchain.block.header',
    'blockchain.block.raw',
    'blockchain.transaction.raw',
    'blockchain.transaction.verbose',
    'blockchain.transaction.send',
    'blockchain.estimatesmartfee',
    'blockchain.supply',
    'blockchain.info',
    'server.status'
]

def dead_response(code=-32600, message="Invalid Request", rid=node_name):
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": rid}

def handle_rpc(raw_data):
    result = {
        "jsonrpc": "2.0",
        "params": [],
        "id": node_name
    }

    error = False
    blank = False
    error_message = ""
    error_code = 0
    isjson = False
    method = ""
    rid = ""

    try:
        try:
            data = json.loads(raw_data)
            isjson = True
        except Exception as e:
            data = parse.parse_qs(raw_data)

        if isjson and data["jsonrpc"] != "2.0":
            error = True
            error_message = "Invalid Request"
            error_code = -32600

        if "method" not in data:
            blank = True
        else:
            method = data["method"] if isjson else data["method"][0]
            if method not in allowed:
                error = True
                error_message = "Invalid Request"
                error_code = -32601

        if "params[]" in data:
            data["params"] = data["params[]"]
            data.pop("params[]", None)

        if "id" in data:
            rid = data["id"] if isjson else data["id"][0]
            if type(rid) is str or type(rid) is int:
                result["id"] = rid

        if error is True:
            result["error"] = {
                "code": error_code,
                "message": error_message
            }
        else:
            if blank:
                result["method"] = "server.status"
            else:
                result["method"] = method
                if "params" in data:
                    result["params"] = data["params"]

    except ValueError:
        result = dead_response(-32700, "Parse error")

    return result


def create_rpc(result_data, rpc_id):
    result = {
        "jsonrpc": "2.0",
        "id": rpc_id
    }

    error = False
    error_message = ""
    error_code = 0

    try:
        if type(result_data) == list or type(result_data) == dict or len(re.findall(r'^[a-fA-F0-9]+$', result_data)) > 0:
            data = result_data

        else:
            error = True
            error_message = "Invalid Request: {}".format(result_data)
            error_code = -32600

        if error is True:
            result["error"] = {
                "code": error_code,
                "message": error_message
            }
        else:
            result["result"] = data
    except Exception as e:
        result = dead_response(-32700, "Parse error")

    return result


class RpcServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    async def send_request(self, request_self, method, params, rid):
        client_port = port
        if method in ["getinfo"]:
            client_port = rpc_port
            
        async with ClientSession('localhost', client_port) as session:
            try:
                response = await session.send_request(method, params, timeout=60)
            except Exception as e:
                response = e

        request_self._set_response()
        request_self.wfile.write(json.dumps(create_rpc(response, rid)).encode('utf-8'))

    def do_GET(self):
        data = handle_rpc(parse.urlparse(self.path).query)
        loop = asyncio.get_event_loop()

        if "error" not in data:
            loop = asyncio.get_event_loop()
            
            try:
                loop.run_until_complete(self.send_request(self, data["method"], data["params"], data["id"]))
            except OSError:
                print('cannot connect - is ElectrumX catching up, not running, or '
                      f'is {port} the wrong RPC port?')
            except Exception as e:
                print(f'error making request: {e}')

        else:
            self._set_response()
            self.wfile.write(json.dumps(dead_response(), indent=4, sort_keys=True).encode('utf-8'))
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = handle_rpc(post_data.decode('utf-8'))

        if "error" not in data:
            loop = asyncio.get_event_loop()
            
            try:
                loop.run_until_complete(self.send_request(self, data["method"], data["params"], data["id"]))
            except OSError:
                print('cannot connect - is ElectrumX catching up, not running, or '
                      f'is {port} the wrong RPC port?')
            except Exception as e:
                print(f'error making request: {e}')

        else:
            self._set_response()
            self.wfile.write(json.dumps(dead_response(), indent=4, sort_keys=True).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=RpcServer, port=4321):
    server_address = ('', port)
    rpcd = server_class(server_address, handler_class)
    print('Starting rpcd on port {}...\n'.format(port))

    try:
        rpcd.serve_forever()
    except KeyboardInterrupt:
        pass

    rpcd.server_close()
    print('Stopping rpcd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
