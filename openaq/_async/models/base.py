from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openaq._async.client import AsyncOpenAQ


class AsyncResourceBase:
    """Base model for async resources.

    Handles the instantiation of the parent client object.


    Attributes:
        client: an instance of OpenAQ async client object.

    """

    def __init__(
        self,
        client: "AsyncOpenAQ",
    ):
        """Initialize the SyncResourceBase.

        Args:
            client (OpenAQ): The client instance to interact with the OpenAQ API.
        """
        self._client = client
