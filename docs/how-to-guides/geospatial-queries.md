# Geospatial Queries

The OpenAQ API provides two methods for querying features with geospatial
features:

1. Point and radius
2. Bounding box

The API documentation describes these methods in detail at:
<https://docs.openaq.org/using-the-api/geospatial>.

!!! warning

    The query parameters for `coordiantes` and `radius` cannot be used with the `bbox`, only one method can be used in a single call. Mixing methods will result in a [`ValidationError`](../reference/exceptions.md#openaq.shared.exceptions.ValidationError) exception.

## Point and radius

The `locations.list()` function exposes the point and radius parameters through
function parameters named `radius` and `coordinates`. The `coordinates`
parameter takes a tuple of floats representing the center point and the `radius`
value represents the distance in meters to search around the the `coordinates`
point. The coordinates point tuple accepts WGS84 coordinates in the form
latitude, longitude (Y,X).

=== "Sync"

    ```py
    import pprint

    from openaq import OpenAQ


    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    locations = client.locations.list(
        coordinates=(13.74433, 100.54365),
        radius=10_000,
        limit=1000
    )
    pprint.pp(locations)
    client.close()
    ```

=== "Async"

    ```py
    import asyncio
    import pprint

    from openaq import AsyncOpenAQ

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        location = await client.locations.list(coordinates=(13.74433,100.54365), radius=10_000, limit=1000)
        pprint.pp(locations)
        await client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```

This will print a list of locations (up to 1,000 per page) within a 10 kilometer radius of the point 13.74433,100.54365, a point in central Bangkok, Thailand.

## Bounding box

The `locations.list()` function also exposes the bounding box parameter through a
function parameters named `bbox`. A bounding box represented a rectangular area represented as a list of WGS84 coordinate values in the order: minimum X, minimum Y, maximum X, maximum Y.

=== "Sync"

    ```py
    import pprint

    from openaq import OpenAQ


    client = OpenAQ(api_key="replace-with-a-valid-openaq-api-key")
    locations = client.locations.list(
        bbox=(5.488869, -0.396881, 5.732144, -0.021973), limit=1000
    )
    pprint.pp(locations)
    client.close()
    ```

=== "Async"

    ```py
    import asyncio
    import pprint

    from openaq import AsyncOpenAQ


    async def main():
        client = AsyncOpenAQ(api_key="replace-with-a-valid-openaq-api-key")
        locations = await client.locations.list(
            bbox=(5.488869, -0.396881, 5.732144, -0.021973), limit=1000
        )
        pprint.pp(locations)
        await client.close()


    if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```

### Generating a bounding box from a polygon

We can generate a bounding box from an aribtrary polygon from a file, such as GeoJSON or Shapefile.

```sh
pip install shapely
```

!!! info

    For this example we use `shapely` but there are many libraries that can provide similar functionality to read and process geospatial data in Python.

For this example

=== "Sync"

    ```py
    from openaq import OpenAQ
    import httpx
    import shapely


    client = OpenAQ(api_key="replace-with-a-valid-openaq-api-key")

    res = httpx.get("https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/7/query?outFields=*&where=1%3D1&f=geojson")

    los_angeles = shapely.from_geojson(res.text)

    locations = client.locations.list(
        bbox=los_angles.bounds, limit=1000
    )
    pprint.pp(locations)
    client.close()
    ```

=== "Async"

    ```py
    import asyncio
    import pprint

    from openaq import AsyncOpenAQ


    async def main():
        client = AsyncOpenAQ(api_key="replace-with-a-valid-openaq-api-key")
        locations = await client.locations.list(
            bbox=(5.488869, -0.396881, 5.732144, -0.021973), limit=1000
        )
        pprint.pp(locations)
        await client.close()


    if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```
