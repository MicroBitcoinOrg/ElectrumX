# Getting started
--------------
We have RESTful API which help you fetch info about MicroBitcoin blockchain and interact with it. This api utilize slightly modified [ElectrumX](http://github.com/MicroBitcoinOrg/ElectrumX/) server as backend.
Our [explorer](https://microbitcoinorg.github.io/explorer) and [web wallet](https://microbitcoinorg.github.io/wallet) uses this api.

# How to use it?
--------------
All request should be send to this endpoint :`https://api.mbc.wiki`

Our api uses **JSON-RPC 2.0** call protocol and you should follow [specification](https://www.jsonrpc.org/specification).
Request object should have following members:

`jsonrpc`: String specifying the version of the JSON-RPC protocol. MUST be exactly "2.0".
*(not mandatory for **GET** request)*

`method`: String containing the name of the method to be invoked.
*(This member is mandatory)*

`params`: Structured value that holds the parameter values to be used during the invocation of the method.
*(This member not mandatory and can be omitted)*

`id`: An identifier established by the Client that MUST contain a String, Number if included.
*(This member not mandatory and can be omitted)*

P.s. keep in mind, that all amounts in this API should be in **Satoshis**.

# Methods
--------------
## blockchain.info
This method return current info about MicroBitcoin blockchain.

Params: none

Request: https://api.mbc.wiki/?method=blockchain.info

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "height": 632543,
    "db_height": 632542,
    "difficulty": 7806.15884578894,
    "bestblockhash": "0000000000063ddd5db865a1d88175aab40372de08feef2d4a737280aba517fa",
    "chain": "main"
  }
}
```
`height`: current network height
`db_height`: height of ElectrumX database
`difficulty`: current network difficulty
`bestblockhash`: hash of latest block
`chain`: name of chain

--------------
## blockchain.address.balance
This method return current balance of specific address.

Params:
`address`: addres, which balance you want to fetch

Request: https://api.mbc.wiki/?method=blockchain.address.balance&params[]=Mbb18MGUuDPnPp2oaAvjACiJzbdndxJ58b

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "confirmed": 137893,
    "unconfirmed": 0
  }
}
```
`confirmed`: confirmed balance
`unconfirmed`: unconfirmed including incoming/outcoming transactions

--------------
## blockchain.address.history
This method return paginated history of specific address. By default return 20 latest transactions. Please, keep in mind that because of limitations of ElectrumX this method not return type of transation *(incoming/outcoming)*.

Params:
`page`: history page, by default set to **0**
`offset`: history pagination offset, by default set to **20**, max value **100**

Request: https://api.mbc.wiki/?method=blockchain.address.history&params[]=Mbb18MGUuDPnPp2oaAvjACiJzbdndxJ58b

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "total": 4,
    "history": [
      {
        "tx_index": 0,
        "data": {
          "txid": "112d42c035f5f03d311706e10efae6b3c85d783fde1d303b3181e4b872d13bdd",
          "size": 4402,
          "version": 2,
          "locktime": 632538,
          "blockhash": "000000000000df9f65c724e57994a8399ad30742e7b8fe0b7862d733c0d17026",
          "height": 632540,
          "confirmations": 62,
          "time": 1539924869,
          "blocktime": 1539924869
        }
      },
      ...
    ]
  }
}
```
`total`: total number of transactions
`history`: array which contain transaction objects

--------------
## blockchain.address.mempool
This method return mempool transactions which was made from specific address 

Params:
`address`: addres, which mempool transactions you want to fetch

Request: https://api.mbc.wiki/?method=blockchain.address.balance&params[]=Ba6PMBPEV3mn9Um3LnZPLLrGXs6g2rYy2v

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": [
    {
      "tx_hash": "25fe4cd607990dce731217235b85ac1ad1caaef28ff5c0c66381005317c321cf",
      "height": 0,
      "fee": 5
    }
  ]
}
```
`tx_hash`: hash of mempool transaction
`height`: always will be **0**, because transaction not included to blockchain (yet)
`fee`: transaction fee

--------------
## blockchain.address.utxo
This method return return **UTXO** (unspent transaction outputs) for specific ammount.

Params: 
`address`: address, which UTXO you want to fetch
`amount`: amount which you want to spend, by default set to **1** Satoshi

Request: https://api.mbc.wiki/?method=blockchain.address.utxo&params[]=Mbb18MGUuDPnPp2oaAvjACiJzbdndxJ58b&params[]=1000

Response: 
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": [
    {
      "tx_hash": "b617ea5b904ac2f327045bbbb2567fbf547fce83d8cb30fac867d10be443d6ea",
      "tx_pos": 59,
      "height": 632178,
      "value": 18829,
      "script": "a9142fb46f2ebfc7ad46cc55ad25e2c7f7de947c98e787"
    }
  ]
}
```
`tx_hash`: hash of transaction
`tx_pos`: position of transaction
`height`: height of block in which this transaction was included
`value`: value of this transaction
`script`: script of this transaction

--------------
## blockchain.block.info
This method return info about block.

Params:
`block_hash`: hash of block
`tx_page`: transactions page, by default set to **0**
`tx_offset`: transactions pagination offset, by default set to **20**, max value **100**

Request: https://api.mbc.wiki/?method=blockchain.block.info&params[]=00000000000972c87fba05727cf482c07c8a06ff5b201f667377f854e7493a30

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "hash": "00000000000972c87fba05727cf482c07c8a06ff5b201f667377f854e7493a30",
    "confirmations": 22,
    "strippedsize": 190,
    "size": 190,
    "weight": 760,
    "height": 632639,
    "version": 536870912,
    "versionHex": "20000000",
    "merkleroot": "f4eedbc566ba4b68bc46f9fb7c17445f604e06bddd9330bd5946e8bc083de1dc",
    "time": 1539931137,
    "mediantime": 1539930948,
    "nonce": 4217536564,
    "bits": "1b0995c8",
    "difficulty": 6837.186485144101,
    "chainwork": "000000000000000000000000000000000000000001e1c64ac25b3ed2b6fa787c",
    "previousblockhash": "000000000005e156a92f555fc82a35f13f1e9826abb4f2ba127468222cbe9acf",
    "nextblockhash": "000000000008baba71b83028f152005584b86126860424da2a9d00b35ad4845b",
    "tx_count": 1,
    "tx": [
      ...
    ]
  }
}
```
`hash`: block hash
`confirmations`: number of block confirmations
`size`: block size in bytes
`height`: block height
`merkleroot`: block merkle root
`time`: block timestamp
`nonce`: block nonce
`difficulty`: block difficulty
`tx_count`: total number of transactions
`tx`: array of block transaction objects

--------------
## blockchain.block.header
This method return block header by index.

Params:
`index`: block index

Request: https://api.mbc.wiki/?method=blockchain.block.header&params[]=600000

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "block_height": 600000,
    "version": 536870912,
    "block_hash": "0000000000045531416ca22a308383e3b1caebbbb87bf232205a79e2984c0936",
    "prev_block_hash": "000000000003ab3a43fae9fe7176f88710a6572e96f865c7c2cb74fde7b7a6b1",
    "merkle_root": "61e8c00ffab88e3e11b5f63a2b8248c3da2078ffd4f7c7812e6df35217f284e9",
    "timestamp": 1537962310,
    "bits": 453432501,
    "nonce": 1573201836
  }
}
```
--------------
## blockchain.block.range
This method return range of block headers. Max **100** headers.

Params:
`start_height`: index from which range starts
`end_height`: index at which range ends

Request: https://api.mbc.wiki/?method=blockchain.block.range&params[]=600000&params[]=600020

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": [
    {
      "block_height": 600000,
      "version": 536870912,
      "block_hash": "0000000000045531416ca22a308383e3b1caebbbb87bf232205a79e2984c0936",
      "prev_block_hash": "000000000003ab3a43fae9fe7176f88710a6572e96f865c7c2cb74fde7b7a6b1",
      "merkle_root": "61e8c00ffab88e3e11b5f63a2b8248c3da2078ffd4f7c7812e6df35217f284e9",
      "timestamp": 1537962310,
      "bits": 453432501,
      "nonce": 1573201836,
      "tx_count": 1,
      "difficulty": 9593.922652674186,
      "size": 315
    },
    ...
  ]
}
```
--------------
## blockchain.transaction.send
This methon broadcast raw signed transaction to MicroBitcoin network.
It's recommended to use this method with **POST** request, because sometimes transaction may contain big amount of inputs/outputs which resut into long transaction hash, which may be not processed because **GET** request URL will be to long.

Params:
`rawtx`: raw signed transaction

Request: https://api.mbc.wiki/?method=blockchain.transaction.send&params[]=02000000010000000000000000000000000000000000000000000000000000000000000000ffffffff180372a709044487c95b08810002aa000000007969696d7000000000000140597307000000001976a914a8fe968f37df9b99727220d9946b1bfb68f1db3188ac00000000

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "txhash": "2a1c421c91e26f0b7c241f52ecc8f8b781dcc4b40fc1025e257963745b18a0fc"
  }
}
```
--------------
## blockchain.transaction.raw
This method return raw transaction.

Params:
`tx_hash`: hash of transaction

Request: https://api.mbc.wiki/?method=blockchain.transaction.raw&params[]=2a1c421c91e26f0b7c241f52ecc8f8b781dcc4b40fc1025e257963745b18a0fc

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "rawtx": "02000000010000000000000000000000000000000000000000000000000000000000000000ffffffff180372a709044487c95b08810002aa000000007969696d7000000000000140597307000000001976a914a8fe968f37df9b99727220d9946b1bfb68f1db3188ac00000000"
  }
}
```
--------------
## blockchain.transaction.verbose
This method return info about transaction.

Params:
`tx_hash`: hash of transaction
`vin_page`: inputs page, by default set to **0**
`vin_offset`: inputs pagination offset, by default set to **20**, max value **100**
`enable_vin_details`: disable details about input spending output, by default set to **1**

Request: https://api.mbc.wiki/?method=blockchain.transaction.verbose&params[]=2a1c421c91e26f0b7c241f52ecc8f8b781dcc4b40fc1025e257963745b18a0fc

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "txid": "2a1c421c91e26f0b7c241f52ecc8f8b781dcc4b40fc1025e257963745b18a0fc",
    "size": 109,
    "version": 2,
    "locktime": 0,
    "vin": [
      ...
    ],
    "vout": [
      ...
    ],
    "blockhash": "000000000004d47d6d473a605cbef61a8f5871d5bbb568518427ffd124c95d79",
    "height": 632690,
    "confirmations": 33,
    "time": 1539934020,
    "blocktime": 1539934020,
    "amount": 125000000,
    "vin_count": 1,
    "vout_count": 1
  }
}
```
`vin`: transaction inputs
`vout`: transaction outputs
`amount`: transfered amount

--------------
## blockchain.estimatesmartfee
This method returns estimated network fee.

Params:
`blocks`: estimated amount of blocks in which transaction should be confirmed, by default set to  **6** *(not mandatory)*

Request: https://api.mbc.wiki/?method=blockchain.estimatesmartfee

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "feerate": 4461,
    "blocks": 6
  }
}
```
--------------
## blockchain.supply
This method return current circulating supply of MicroBitcoin.

Params:
`height`: specific height for circulating supply *(not mandatory, by default set to current height)*

Request: https://api.mbc.wiki/?method=blockchain.supply

Response:
```
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "height": 632755,
    "supply": 1824714250000000,
    "halvings_count": 2,
    "reward": 12500
  }
}
```
`supply`: circulating supply
`halvings_count`: number of halvings
`reward`: reward per block

# Conclusion
You can use this thread if you have any questions or ideas how to improve this API :)

P.s. You can set up your own MicroBitcoin API using out [ElectrumX](https://github.com/MicroBitcoinOrg/ElectrumX/) repository :D !
