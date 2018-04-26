# blockchain
a simple blockchain written in python (forked from dvf/blockchain)

test 1.0 
  In this version ,I add some new features in my codes.
    
    1.try to use a concept of memorypool
    2.change the consensus mechanism
      Currently,the cryptocurrency using POW are facing a predicament of low-output,like bitcoin.
      For this reason, it is necessary to come up with a mechanism to improve POW.
      Although.....the current code is far from the POW used by Bitcoin.  ->.->
      My(tutor's) solution is 
      When a miner digs into the “mine” and the volume of transactions in the memory pool is greater than the extent of the block can           accommodate, by signing the transaction and “hanging” it on the current block, the miner can package more transactions.
      My implementation is to add a transaction collection (very simple).... 
      In this case, isn't it easier to change the size of the block? 
      Because.....
      the requirements for Graduation Project are to study an original and innovative method....
    
  在这个版本中，我加了一些新的特征
    1.尝试使用内存池
    2.改变原有的共识机制
      目前，使用POW共识机制的加密货币如比特币，面临着低吞吐量的困境，为此，有必要想出一种改善POW的机制。
      虽然当前代码和比特币使用的POW相距甚远.....->.-> 
      我(dao)的(shi)解决办法是
      当矿工挖到“矿” 且 内存池中的交易量大于块可容纳的程度时，通过对交易进行签名，并将其“挂”在当前的块上，矿工可以打包更多的交易。
    
      我的实现是在添加一个交易集合(很简单的方式).... 这样的话，改变块的大小不是更方便嘛？因为，毕设要求就是研究一种独创、新颖的方法啊.....
