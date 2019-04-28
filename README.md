# cc-orderbook-python
An example of keeping Bitfinex order book

To list arguments:
```
python run_me.py -h
```

## Bitfinex Features
Bitfinex feed feature has one specific. The batch of changes look as a sequence of changes with the same timestamp. 
Usually first come changes which remove levels, some times bids or asks can been even empty, 
then come changes which add levels, and eventualy the book is filled.   

Therefore, the on_change event is called only at the end of batch when the book is filled.
