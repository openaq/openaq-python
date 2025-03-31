# Working with API rate limits

OpenAQ limits the number of API requests you can make in a set time to ensure
fair access for all users and prevent overuse.

A more detailed overview of the API rate limits is also available at the main
documentation site:

<https://docs.openaq.org/using-the-api/rate-limits>

With each response the OpenAQ API returns HTTP headers with rate limit
information. The OpenAQ Python SDK also exposes these values through the
`headers` field in the response object.

```pycon hl_lines="5"
>>> from openaq import OpenAQ
...
>>> client = OpenAQ()
>>> locations = client.locations.list()
>>> print(locations.headers)
Headers(
    x_ratelimit_limit=60,
    x_ratelimit_remaining=59,
    x_ratelimit_used=1,
    x_ratelimit_reset=58
)
```

The OpenAQ Python SDK automatically tracks these headers internally. If the rate
limit has been exceeded the client will throw a `RateLimitError` exception. Once
the rate limit reset period has passed the client will send requests up to
allotted rate limit amount and period.
