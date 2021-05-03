# censuscoding

## Usage

### Download raw E911 data for censuscoding

`censuscoding download <state>`

Censuscoding uses publicly available E911 data to map addresses to lat/lon coordinates. For example, E911 data in Rhode Island is available from: https://www.rigis.org/datasets/e-911-sites

Lat/lon coordinates are mapped to US Census blockgroups using the TIGER database: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

The `download` will automatically download these files for you and store them in the `censuscoding` package directory. By default, censuscoding will not redownload files you have already downloaded, unless you use the `censuscoding download --update <state>` command.

Once the E911 and TIGER files are downloaded, censuscoding creates a deterministic mapping from all street names by zip code and city name to the blockgroup that contains them.

### Censuscode a csv file of addresses

Run `censuscoding code -h` to see full options.
