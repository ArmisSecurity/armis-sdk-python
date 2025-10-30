Welcome to the documentation of the **Armis Python SDK**!

This website will provide you all the information you'll need to interact with the SDK.

## Installation
Use your favourite package manager to install the SDK, for example:
```shell linenums="1"
pip install armis_sdk
```
## Usage

All interaction with the SDK happens through the [ArmisSdk][armis_sdk.core.armis_sdk.ArmisSdk] class. You'll need a few things:

1. **Tenant name**: The name of the tenant you want to interact with.
2. **Secret key**: The secret key associated with the tenant, obtained from the tenant itself.
3. **Client id**: A unique identifier for you application. Currently, this can be any string.
4. **(optional) Base domain**: The base domain of you tenant, defaults to `armis.com`,

You can either provide these values using the environment variables `ARMIS_TENANT`, `ARMIS_SECRET_KEY`, `ARMIS_CLIENT_ID`, and `ARMIS_BASE_DOMAIN`:
```python linenums="1"
from armis_sdk import ArmisSdk

armis_sdk = ArmisSdk()
```

or by passing them explicitly:
```python linenums="1"
from armis_sdk import ArmisSdk

armis_sdk = ArmisSdk(tenant="<tenant>", secret_key="<secret_key>", client_id="<client_id>", base_domain="<base_domain>")
```
!!!tip

    If you're building an application that interacts with multiple tenants, you can populae only the `ARMIS_CLIENT_ID` environment variable and pass the `tenant` and `secret_key` explicitly:
    ```python linenums="1"
    from armis_sdk import ArmisSdk

    armis_sdk = ArmisSdk(tenant="<tenant>", secret_key="<secret_key>")
    ```

## Entity clients
Once you have an instance of [ArmisSdk][armis_sdk.core.armis_sdk.ArmisSdk], 
you can start interacting with the various clients, each handles use-cases of a specific entity.


!!! info

    Note that all functions in this SDK that eventually make HTTP requests are asynchronous.

    However, for convenience, all public asynchronous functions can also be executed in a synchronous way.


For example, if you want to update a site's location:
```python linenums="1" hl_lines="10"
import asyncio

from armis_sdk import ArmisSdk
from armis_sdk.entities.site import Site

armis_sdk = ArmisSdk()

async def main():
    site = Site(id="1", location="new location")
    await armis_sdk.sites.update(site)

asyncio.run(main())
```
