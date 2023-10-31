The OpenAQ API supports pagination to allow fetching of large amounts of data through smaller pages of results. Pagination is controlled through the `page` and `limit` query parameters. All resource `list()` methods in OpenAQ Python provide access to these query parameters through keyword arguments. These values default to `page=1` and `limit=1000`. 

For many result sets in the API we can use the `found` value from the response `meta` object to find the total number of pages to loop through.

```py hl_lines="9"
from math import ceil

from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

locations = client.locations.list()
meta = locations.meta
found = meta.found

limit = 1000

for i in range(found/limit):
    locations.client.list(limit=limit, page=i)
```

We can then divide the value in `found` by the chosen `limit` value and round up any remainder with `math.ceil` to get the total number of pages. We can then use that value to loop through all the result pages.

```py hl_lines="13-16"
from math import ceil

from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

locations = client.locations.list()
meta = locations.meta
found = meta.found

limit = 1000

pages = ceil(found/limit)

for i in pages:
    client.locations.list(limit=limit, page=i)
```

For large result sets such as in measurements the `meta` `found` value will provide an estimate, not the actual number of results. For this we can use a different pattern, looping through the pages until we encounter a page with no results.

```py hl_lines="13-17"
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

locations = client.measurements.list()

limit = 1000

results = True

page_num = 1

while results:
    measurements = client.measurements.list(limit=limit, page=page_num)
    if len(measurements.results) == 0:
        results = False
    page_num += 1
```