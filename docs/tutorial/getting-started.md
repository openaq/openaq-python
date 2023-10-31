

In this tutorial, we will learn how to install and setup the OpenAQ API Python wrapper and query a location from the OpenAQ API .


## Install OpenAQ Python

With Python and pip installed on our system we can install the OpenAQ Python API wrapper via pip.

```sh
pip install openaq
```


## Register for an OpenAQ API Key

Visit [api.openaq.org/register](https://api.openaq.org/register).


!!! warning

    For this tutorial we will use a _placeholder_ API Key: 'replace-with-a-valid-openaq-api-key'. __Do not__ use this API key in your code, it will not work. Replace the placeholder value with the key you receive after signing up.


## The Code


We will now walkthrough the following code to access a single monitoring location from the OpenAQ API.

```py
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

location = client.locations.get(2178)

client.close()

print(location)
```


### Step 1: Import the OpenAQ class from openaq.

```py hl_lines="1"
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

location = client.locations.get(2178)

client.close()

print(location)
```

`OpenAQ` is a Python class that provides access to communicate with API resources.

### Step 2: Instantiate the client.

```py hl_lines="3"
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

location = client.locations.get(2178)

client.close()

print(location)
```

Here the `client` variable will be an "instance" of the class `OpenAQ`.

This will be the main variable we will use to interact with API.

### Step 3: Call the locations get with a locations ID of 2178.

```py hl_lines="5"
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

location = client.locations.get(2178)

client.close()

print(location)
```

Within the client we access the `locations` resource and call the `get` method to retrieve a single location by its ID


### Step 4: Close the client connection.

```py hl_lines="7"
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

location = client.locations.get(2178)

client.close()

print(location)
```

We close the client to ensure connections are properly cleaned up.


### Step 5: Print the results.

```py hl_lines="9"
from openaq import OpenAQ

client = OpenAQ(api_key='replace-with-a-valid-openaq-api-key')

location = client.locations.get(2178)

client.close()

print(location)
```

We print the results to our console to see the data from the requested location.

The output should look something like this:

> ```
LocationsResponse(meta=Meta(name='openaq-api', website='/', page=1, limit=100, found=1), results=[Location(id=2178, name='Del Norte', locality='Albuquerque', timezone='America/Denver', country=CountryBase(id=13, code='US', name='United States of America'), owner=OwnerBase(id=4, name='Unknown Governmental Organization'), provider=ProviderBase(id=119, name='AirNow'), is_mobile=False, is_monitor=True, instruments=[InstrumentBase(id=2, name='Government Monitor')], sensors=[SensorBase(id=3917, name='o3 ppm', parameter=ParameterBase(id=10, name='o3', units='ppm', display_name='O₃')), SensorBase(id=3916, name='no2 ppm', parameter=ParameterBase(id=7, name='no2', units='ppm', display_name='NO₂')), SensorBase(id=25227, name='co ppm', parameter=ParameterBase(id=8, name='co', units='ppm', display_name='CO')), SensorBase(id=3919, name='pm10 µg/m³', parameter=ParameterBase(id=1, name='pm10', units='µg/m³', display_name='PM10')), SensorBase(id=4272226, name='no ppm', parameter=ParameterBase(id=35, name='no', units='ppm', display_name='NO')), SensorBase(id=4272103, name='nox ppm', parameter=ParameterBase(id=19840, name='nox', units='ppm', display_name='NOx')), SensorBase(id=3918, name='so2 ppm', parameter=ParameterBase(id=9, name='so2', units='ppm', display_name='SO₂')), SensorBase(id=3920, name='pm25 µg/m³', parameter=ParameterBase(id=2, name='pm25', units='µg/m³', display_name='PM2.5'))], coordinates=Coordinates(latitude=35.1353, longitude=-106.584702), bounds=[-106.584702, 35.1353, -106.584702, 35.1353], distance=None, datetime_first=Datetime(utc='2016-03-06T19:00:00+00:00', local='2016-03-06T12:00:00-07:00'), datetime_last=Datetime(utc='2023-10-31T13:00:00+00:00', local='2023-10-31T07:00:00-06:00'))])
```

## Conclusion

You have now successfully requested and downloaded data from the OpenAQ API with the OpenAQ Python wrapper. To learn more check out the [how-to guides](/how-to-guides/working-with-the-client/) and [reference](/reference/openaq/) documentation.