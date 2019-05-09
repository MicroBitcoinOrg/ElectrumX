#!/usr/bin/env python3
"""
Usage::
    ./rpcd.py [<port>]
"""
from aiorpcx import ClientSession
from urllib import parse
from os import environ
from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import json as sanic_json
import json
import re


API_ID = 'ElectrumX API'
RPC_PORT = int(environ.get('RPC_PORT', 7403))
SERVER_PORT = 4321
ALLOWED = [
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


def dead_response(code=-32600, message="Invalid Request", rid=API_ID):
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": rid}


def handle_rpc(data, ispost=False):
    result = {
        "jsonrpc": "2.0",
        "params": [],
        "id": API_ID
    }

    error = False
    blank = False
    error_message = ""
    error_code = 0
    method = ""
    rid = ""

    try:
        if ispost and data["jsonrpc"] != "2.0":
            error = True
            error_message = "Invalid Request"
            error_code = -32600

        if "method" not in data:
            blank = True
        else:
            method = data["method"] if ispost else data["method"][0]
            if method not in ALLOWED:
                error = True
                error_message = "Invalid Request"
                error_code = -32601

        if "params[]" in data:
            data["params"] = data["params[]"]
            data.pop("params[]", None)

        if "params" not in data:
            data["params"] = []

        if "id" in data:
            rid = data["id"] if ispost else data["id"][0]
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

    except:
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


class RpcServer(HTTPMethodView):
    async def send_request(self, request_self, method, params, rid):
        async with ClientSession('localhost', RPC_PORT) as session:
            try:
                response = await session.send_request(method, params, timeout=60)
            except Exception as e:
                response = e

        return create_rpc(response, rid)


    async def get(self, request):
        data = handle_rpc(parse.parse_qs(request.query_string))
        headers = {'Access-Control-Allow-Origin': '*'}

        if "error" not in data:
            try:
                result = await self.send_request(self, data["method"], data["params"], data["id"])
                return sanic_json(result, headers=headers)
            except OSError:
                print('cannot connect - is ElectrumX catching up, not running, or '
                      f'is {RPC_PORT} the wrong RPC port?')
            except Exception as e:
                print(f'error making request: {e}')

        else:
            return sanic_json(dead_response(), headers=headers)


    async def post(self, request):
        data = handle_rpc(request.json, True)
        headers = {'Access-Control-Allow-Origin': '*'}

        if "error" not in data:
            try:
                result = await self.send_request(self, data["method"], data["params"], data["id"])
                return sanic_json(result, headers=headers)
            except OSError:
                print('cannot connect - is ElectrumX catching up, not running, or '
                      f'is {RPC_PORT} the wrong RPC port?')
            except Exception as e:
                print(f'error making request: {e}')

        else:
            return sanic_json(dead_response(), headers=headers)


def run(server_port=SERVER_PORT):
    app = Sanic()
    app.add_route(RpcServer.as_view(), '/')
    app.run(host='0.0.0.0', port=server_port)


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(int(argv[1]))
    else:
        run()
complete(self.send_request(self, data["method"], data["params"], data["id"]))
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
