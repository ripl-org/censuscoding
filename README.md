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

## Contributors
* [Mark Howison](https://mark.howison.org/)
* [Daniel Molitor](https://dmolitor.github.io)

## License

`censuscoding` is freely available for non-commercial use under the license provided in [LICENSE](https://github.com/ripl-org/censuscoding/blob/main/LICENSE).
To inquiry about commercial use, please contact [connect@ripl.org](mailto:connect@ripl.org).

## Data

Data included in the `censuscoding` package were derived from the following sources:

### Rhode Island Geographic Information System E911 Site/Structure Address Points

Version [e911Sites21r1](https://www.arcgis.com/sharing/rest/content/items/2d9f7e30ef904317b29f735723127c94/info/metadata/metadata.xml?format=default&output=html).

> These data are designed and maintained for RI E 9-1-1 mapping software. They are not intended for any other purpose. This dataset is provided 'as is.’ The producer(s) of this dataset, contributors to this dataset, the Rhode Island Geographic Information System (RIGIS) consortium, the State of Rhode Island, and the University of Rhode Island do not make any warranties of any kind for this dataset, and are not liable for any loss or damage however and whenever caused by any use of this dataset. Please acknowledge both RIGIS and the primary producer(s) of this dataset in any derived products. Versions of the RIGIS logo suitable for both printed and web-based products are available at https://www.rigis.org.

### US Census Bureau TIGER/Line Shapefiles

Version [2020](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2020.html).
