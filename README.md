# censuscoding

<!-- badges: start -->
![](https://github.com/ripl-org/censuscoding/actions/workflows/censuscoding.yml/badge.svg)
<!-- badges: end -->

`censuscoding` is a self-contained tool for determining the Census 
blockgroup for a street address. It is developed by
[Research Improving People's Lives (RIPL)](https://ripl.org).

## License

Copyright 2021-2023 Innovative Policy Lab d/b/a Research Improving People's Lives
("RIPL"), Providence, RI. All Rights Reserved.

Your use of the Software License along with any related Documentation, Data,
etc. is governed by the terms and conditions which are available here:
[LICENSE.md](https://github.com/ripl-org/censuscoding/blob/main/LICENSE.md)

Please contact [connect@ripl.org](mailto:connect@ripl.org) to inquire about
commercial use.

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

## Contributors
* [Mark Howison](https://mark.howison.org/)
* [Daniel Molitor](https://dmolitor.github.io)

## Data

Data included in the `censuscoding` package come from many sources, described
in the complementary [censuscoding-data](https://github.com/ripl-org/censuscoding-data)
repository.
