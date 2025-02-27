# Working with API rate limits

OpenAQ limits the number of API requests you can make in a set time to ensure
fair access for all users and prevent overuse.

A more detailed overview of the API rate limits is also available at the main
documentation site:

<https://docs.openaq.org/using-the-api/rate-limits>

With each response the OpenAQ API returns HTTP headers with rate limit
information. The OpenAQ Python SDK also exposes these values through the
`headers` field in the response object.

The following example code demonstrates one method of how to gracefully handle
rate limits when interacting with the OpenAQ Python SDK. When the rate limit is
approached, the script pauses execution for a specified duration, defined by the
X-Rate-Limit-Remaining header, allowing the rate limit to reset before
proceeding with further requests. This proactive approach prevents unexpected
API errors and ensures seamless integration with the OpenAQ service.


To demonstrate this technique we will list locations that measurement PM<sub>2.5</sub> 

=== "Sync"

    ```py hl_lines="10"
    from openaq import OpenAQ

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    page = 1
    remaining = 60
    locations = client.locations.list(parameters_id=2, limit=1000, page=page)
    for location in locations.results:
        print(f"fetching latest from location {location.id}")
        response = client.locations.latest(location.id)
        remaining = response.headers.x_ratelimit_remaining
        page += 1
        if remaining == 0:
            reset = response.headers.x_ratelimit_reset
            print(f"Rate limit reached. Waiting for {reset} seconds...")
            time.sleep(reset)
            remaining = 60
    client.close()
    ```

=== "Async"

    ```py hl_lines="13"
    import asyncio

    from openaq import AsyncOpenAQ

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        page = 1
        remaining = 60
        locations = await client.locations.list(parameters_id=2, limit=1000, page=page)
        for location in locations.results:
            print(f"fetching latest from location {location.id}")
            response = await client.locations.latest(location.id)
            remaining = response.headers.x_ratelimit_remaining
            page += 1
            if remaining == 0:
                reset = response.headers.x_ratelimit_reset
                print(f"Rate limit reached. Waiting for {reset} seconds...")
                await asyncio.sleep(reset)
                remaining = 60
        client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```


=== "Sync"

    ```py hl_lines="12"
    from openaq import OpenAQ

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    page = 1
    remaining = 60
    locations = client.locations.list(parameters_id=2, limit=1000, page=page)
    for location in locations.results:
        print(f"fetching latest from location {location.id}")
        response = client.locations.latest(location.id)
        remaining = response.headers.x_ratelimit_remaining
        page += 1
        if remaining == 0:
            reset = response.headers.x_ratelimit_reset
            print(f"Rate limit reached. Waiting for {reset} seconds...")
            time.sleep(reset)
            remaining = 60
    client.close()
    ```

=== "Async"

    ```py hl_lines="15"
    import asyncio

    from openaq import AsyncOpenAQ

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        page = 1
        remaining = 60
        locations = await client.locations.list(parameters_id=2, limit=1000, page=page)
        for location in locations.results:
            print(f"fetching latest from location {location.id}")
            response = await client.locations.latest(location.id)
            remaining = response.headers.x_ratelimit_remaining
            page += 1
            if remaining == 0:
                reset = response.headers.x_ratelimit_reset
                print(f"Rate limit reached. Waiting for {reset} seconds...")
                await asyncio.sleep(reset)
                remaining = 60
        client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```



=== "Sync"

    ```py hl_lines="13"
    from openaq import OpenAQ

    client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')
    page = 1
    remaining = 60
    locations = client.locations.list(parameters_id=2, limit=1000, page=page)
    for location in locations.results:
        print(f"fetching latest from location {location.id}")
        response = client.locations.latest(location.id)
        remaining = response.headers.x_ratelimit_remaining
        page += 1
        if remaining == 0:
            reset = response.headers.x_ratelimit_reset
            print(f"Rate limit reached. Waiting for {reset} seconds...")
            time.sleep(reset)
            remaining = 60
    client.close()
    ```

=== "Async"

    ```py hl_lines="16"
    import asyncio

    from openaq import AsyncOpenAQ

    async def main():
        client = AsyncOpenAQ(api_key='replace-with-a-valid-openaq-api-key')
        page = 1
        remaining = 60
        locations = await client.locations.list(parameters_id=2, limit=1000, page=page)
        for location in locations.results:
            print(f"fetching latest from location {location.id}")
            response = await client.locations.latest(location.id)
            remaining = response.headers.x_ratelimit_remaining
            page += 1
            if remaining == 0:
                reset = response.headers.x_ratelimit_reset
                print(f"Rate limit reached. Waiting for {reset} seconds...")
                await asyncio.sleep(reset)
                remaining = 60
        client.close()

    if __name__ ==  '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    ```


The example above demonstrates just one method managing API call rate with the
use of the rate limit headers. The values available in the rate limit headers
provide a lot of information to predictable handle the API rate limit and avoid
errors in your code.
