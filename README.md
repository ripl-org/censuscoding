# censuscoding

<!-- badges: start -->
![](https://github.com/ripl-org/censuscoding/actions/workflows/censuscoding.yml/badge.svg)
<!-- badges: end -->

`censuscoding` is a self-contained tool for determining the Census 
blockgroup for a street address. It is developed by
[Research Improving People's Lives (RIPL)](https://ripl.org).

## Installation

Due to outstanding bugs in dependencies introduced in Python 3.10.0,
`censuscoding` requires Python >=3.7 and <3.10.

To install from PyPI using **pip**:  
`pip install censuscoding`

To install a **development version** from the current directory:  
`pip install -e .`

## Running
There is a single command line script included, `censuscoding`.

`censuscoding` supports the following arguments:
* `--input` or `-i` - path to an input CSV file containing columns `record_id`, `zip_code`, and `address`
* `--output` or `-o` - path to output CSV file containing `record_id`, `zip_code`, `blkgrp`
* `--record_id` - field name corresponding to the record ID (default: 'record_id')
* `--zip_code` - field name corresponding to the zip code (default: 'zip_code')
* `--address` - field name corresponding to the street address with street name and number (default: 'address')

## Authors
* [Mark Howison](https://mark.howison.org/)
* [Daniel Molitor](https://dmolitor.github.io)
