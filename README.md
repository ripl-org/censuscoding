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

To `censuscoding` is freely available for non-commercial use under the license provided in [LICENSE](https://github.com/ripl-org/censuscoding/blob/main/LICENSE).
To inquiry about commercial use, please contact [connect@ripl.org](mailto:connect@ripl.org).

The derived data packaged with `censuscoding` is covered under this license, however PLEASE CAREFULLY READ THE DATA SECTION BELOW FOR IMPORTANT INFORMATION ON THE COMPLEX LICENSING OF THE MANY ORIGINAL DATA SOURCES USED TO DERIVE THIS DATA.

## Data

Data included in the `censuscoding` package are derived from combining the US Census Bureau's TIGER/Line shapefiles version [2020](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2020.html) at the block group level with a large collection of address point data from state and county governments across the US, which are indexed by the [OpenAddresses](https://openaddresses.io/) open data project.

The TIGER/Line data are in the public domain. **The address point data are licensed under many different terms and conditions**, which are summarized in the [SOURCES](https://github.com/ripl-org/censuscoding-data/blob/main/SOURCES.md) file in the `censuscoding-data` repository.

We acknowledge the following government agencies who have published the address point data that are critical to the development of this project:

**State Offices**
* [Colorado Governor's Office of Information Technology](https://oit.colorado.gov/)
* [Maine Office of GIS](https://www.maine.gov/megis/)
* [Massachusetts Bureau of Geographic Information (MassGIS)](https://www.mass.gov/orgs/massgis-bureau-of-geographic-information)
* [New Jersey Office of GIS](https://njgin.nj.gov/njgin/about/ogis)
* [Rhode Island Geographic Information System](https://www.rigis.org)

**County/Municipal Offices**
* [Honolulu Land Information System (HoLIS)](https://www.honolulugis.org/)
