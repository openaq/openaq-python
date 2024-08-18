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

The OpenAQ API key can be passed directly as an argument on the creation of the client as shown above. Alternatively we can use the `OPENAQ_API_KEY` environment variable to set the api_key value without directly setting the value on client instantiation. e.g.:

```sh
OPENAQ_API_KEY=my-openaq-api-key python main.py
```

Where `main.py` is something like:

=== "Sync"

    ```py title="main.py"
    from openaq import OpenAQ

    client = OpenAQ()
    # client.api_key will be 'my-openaq-api-key per' the OPENAQ_API_KEY
    # environment variable
    ```

=== "Async"

    ```py title="main.py"
    from openaq import AsyncOpenAQ

    client = AsyncOpenAQ()
    # client.api_key will be 'my-openaq-api-key' per the OPENAQ_API_KEY
    # environment variable
    ```

Setting the API key via the client class argument on instantiation will also supercede the implicit setting of `api_key` through the `OPENAQ_API_KEY` environment variable.

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

    from openaq import AsyncOpenAQ

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

    from openaq import AsyncOpenAQ

    async def main():
        async with AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key') as client:
            await client.locations.get(2178)

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```

### API key

An API Key is required to make requests with the OpenAQ API.

We can add an API Key to OpenAQ Python one of two ways. As shown above, the API key string can be directly passed when instantiating the `OpenAQ` or `AsyncOpenAQ` class via the `api_key` argument. Alternatively if a key is not passed to the constructor `OpenAQ` and `AsyncOpenAQ` will automatically look for a system environment variable named `OPENAQ-API-KEY` and set the value of that to the `api_key` argument. Directly passing a value to the `api_key` argument in the client constructors will always override an environment variable.
