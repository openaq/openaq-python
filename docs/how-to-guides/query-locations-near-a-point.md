The OpenAQ API provides a query parameters for querying monitoring locations
near a geographic point. The `locations.list()` functions exposes these
parameters through function parameters named, `radius` and `coordinates`. The
`coordinates` parameter takes a tuple of floats representing the center point and the `radius` value represents the distance in meters to search around the the `coordinates` point. The coordinates point tuple accepts WGS84 coordinates in the form latitude, longitude (Y,X).

=== "Sync"

    ```py
    from openaq import OpenAQ

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    client.locations.list(coordinates=(), radius=10_000)
    client.close()
    ```

=== "Async"

    ```py
    import asyncio

    from openaq import AsyncOpenAQ

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        await client.locations.list(coordinates=(), radius=10_000)
        await client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```

!!! info

    The OpenAQ API also provides parameters for querying within a geographic bounding box. The query parameters for `coordiantes` and `radius` cannot be used with the `bbox`, only one method can be used in a single call. Mixing method will result in a `ValidationError` exception. See the [Query locations inside a polygon](query-locations-inside-a-polygon) guide.
