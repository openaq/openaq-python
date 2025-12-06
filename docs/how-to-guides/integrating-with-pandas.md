# Integrating with Pandas

The OpenAQ Python SDK is designed around native Python data structures
and in turn does not return data as vectorized arrays such as data frames used
by packages like Numpy, Pandas and others. Because native Python data structures
are used integrating these types of libraries is straightforward.

Because the data returned from the OpenAQ API is highly nested as a deserialized
Python object we need to flatten the resulting response so that it fits as a
2-dimensional array in Pandas. Fortunately, Pandas provides a function to
facilitate this, `json_normalize`:

=== "Sync"

    ```py
    from openaq import OpenAQ
    from pandas import json_normalize

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    response = client.locations.list(
        bbox=[-0.464172,5.449908,0.030212,5.691491]
    )
    data = response.dict()
    df = json_normalize(data['results'])
    client.close()
    ```

=== "Async"

    ```py
    import asyncio

    from openaq import AsyncOpenAQ
    from pandas import json_normalize

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        response = await client.locations.list(
            bbox=[-0.464172,5.449908,0.030212,5.691491]
        )
        data = response.dict()
        df = json_normalize(data['results'])
        await client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```
