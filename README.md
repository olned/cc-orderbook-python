# cc-orderbook-python
An example of keeping Bitfinex order book

To list arguments:
```
python run_me.py -h
```

## Requirements
Python >= 3.6

Python >= 3.7.3 is needed to run parser_book.py 

## Measurements
The process of feeding and maintaining a book of orders can be divided into 5 parts. This way we have five measurement 
parameters::
1. webcast transmission
2. unpacking and routing the received message
3. processing the message and making changes to the order book
4. packaging and transferring a snapshot of a book to a message queue (simulation)
5. receiving and unpacking a snapshot from the message queue (simulation) 

## Bitfinex Features
Bitfinex feed feature has one specific. The batch of changes look as a sequence of changes with the same timestamp. 
Usually first come changes which remove levels, some times bids or asks can been even empty, 
then come changes which add levels, and eventualy the book is filled.   

Therefore, the on_change event is called only at the end of batch when the book is filled.
