from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openaq._sync.client import OpenAQ


class SyncResourceBase:
    """Base model for sync resources.

    Handles the instantiation of the parent client object.


    Attributes:
        client: an instance of OpenAQ client object.

    """

    def __init__(
        self,
        client: "OpenAQ",
    ):
        """Initialize the AsyncResourceBase.

        Args:
            client (OpenAQ): The client instance to interact with the OpenAQ API.
        """
        self._client = client
