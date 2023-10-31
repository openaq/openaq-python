## Create an instance of the client

OpenAQ Python provides a synchronous client via the `OpenAQ` class and an asynchronous client via the `AsyncOpenAQ` class, for working with `async`/`await` within event loops. This guide will show the options on how to create an instance of the client class.


=== "Sync"

    ```py
    from openaq import OpenAQ

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    ```

=== "Async"

    ```py
    from openaq import AsyncOpenAQ

    client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    ```



`openaq` uses [httpx](https://www.python-httpx.org/) under-the-hood to make http calls to the OpenAQ API. The OpenAQ client follows the same pattern as [httpx](https://www.python-httpx.org/) for opening and closing connections. Once the client is instantiated an `httpx.Client` (or `httpx.AsyncClient`) is opened and must be explicitly closed after use. This allows for more efficient usage of network resources by maintaining an open connection.


=== "Sync"

    ```py
    from openaq import OpenAQ

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    client.locations.get(2178)
    client.close()
    ```

=== "Async"

    ```py
    import asyncio

    from openaq import OpenAQ

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        await client.locations.get(2178)
        await client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```


Alternatively we can use a context manager to handle closing the connection for us:


=== "Sync"

    ```py
    from openaq import OpenAQ

    with OpenAQ(api_key='replace-with-a-valid-openaq-api-key') as client:
        client.locations.get(2178)
    ```

=== "Async"

    ```py
    import asyncio

    from openaq import OpenAQ

    async def main():
        async with AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key') as client:
            await client.locations.get(2178)

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```

