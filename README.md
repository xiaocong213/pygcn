# PyGCN
Anonymous VOEvent client for receiving GCN/TAN notices in XML format

This is fork of [Leo Singer's PyGCN](https://github.com/lpsinger/pygcn). We recommend that you read the [original repository's README](https://github.com/lpsinger/pygcn#pygcn)

## Features and Differences
Here we note the features this fork provides that differs from the original PyGCN:

1. VOEvent Parser (`gcn/voeventparser.py`)

    Parses VOEvent XML data
    
    Currently only supported for the following senders:
    * AMON 
    * Fermi
    * LVC

2. MySQL Database Handler

3. GCN Followup (`gcn/gcnfollowup.py`)
    
    An example of a followup procedure for the [KAIT telescope](http://w.astro.berkeley.edu/bait/kait.html).
    

## Installation

To install PyGCN, simply run:

    $ pip install --user pygcn

## Usage

PyGCN provides an example script called `pygcn-listen` that will simply write
all VOEvents that it receives to files in the current directory. To try it out,
simply run:

    $ pygcn-listen

and then type Control-C to quit.

