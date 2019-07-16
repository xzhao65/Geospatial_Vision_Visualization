# Assignment 3 Aerial Image Retrieval

This is a program aim to query, download and stitch images from Bing Map Tile System, for retrieving required area of interest.

## Required Packages

```
from urllib import request
import math
import sys
from PIL import Image
import os
```

## Attentions

Do not query a large area. Memory limit and query limit will lead to failure. Too many query will lead to IP ban.


## Usage

```
python aerail_image_retrieval.py {lat1} {lon1} {lat2} {lon2}
```
