# Armis SDK for Python 3.9+
[![Run tests](https://github.com/ArmisSecurity/armis-sdk-python/actions/workflows/test.yml/badge.svg)](https://github.com/ArmisSecurity/armis-sdk-python/actions/workflows/test.yml)
[![Run formatter](https://github.com/ArmisSecurity/armis-sdk-python/actions/workflows/format.yml/badge.svg)](https://github.com/ArmisSecurity/armis-sdk-python/actions/workflows/format.yml)
[![Run linter](https://github.com/ArmisSecurity/armis-sdk-python/actions/workflows/lint.yml/badge.svg)](https://github.com/ArmisSecurity/armis-sdk-python/actions/workflows/lint.yml)

The Armis SDK is a package that encapsulates common use-cases for interacting with the [Armis platform](https://www.armis.com/).

## Installation
Use your favourite package manager to install the SDK, for example:
```shell
pip install armis_sdk
```

## Documentation
For full documentation, please visit our [dedicated](https://armis-python-sdk.readthedocs.io) site.

## Usage

All interaction with the SDK happens through the `ArmisSdk` class. You'll need 3 things:

1. **Tenant name**: The name of the tenant you want to interact with.
2. **Secret key**: The secret key associated with the tenant, obtained from the tenant itself.
3. **Client id**: A unique identifier for you application. Currently, this can be any string.

You can either provide these values using the environment variables `ARMIS_TENANT`, `ARMIS_SECRET_KEY`, and `ARMIS_CLIENT_ID`:
```python
from armis_sdk import ArmisSdk

armis_sdk = ArmisSdk()
```

or by passing them explicitly:
```python
from armis_sdk import ArmisSdk

armis_sdk = ArmisSdk(tenant="<tenant>", secret_key="<secret_key>", client_id="<client_id>")
```

> [!TIP]
> If you're building an application that interacts with multiple tenants, you can populae only the `ARMIS_CLIENT_ID` environment variable and pass the `tenant` and `secret_key` explicitly:
> ```python
> from armis_sdk import ArmisSdk
>
> armis_sdk = ArmisSdk(tenant="<tenant>", secret_key="<secret_key>")
> ```

## Entity clients
Once you have an instance of `ArmisSdk`, you can start interacting with the various clients, each handles use-cases of a specific entity.


> [!NOTE]
> Note that all functions in this SDK that eventually make HTTP requests are asynchronous.
> 
> However, for convenience, all public asynchronous functions can also be executed in a synchronous way. 

For example, if you want to update a site's location:
```python
import asyncio

from armis_sdk import ArmisSdk
from armis_sdk.entities.site import Site

armis_sdk = ArmisSdk()

async def main():
    site = Site(id="1", location="new location")
    await armis_sdk.sites.update(site)

asyncio.run(main())
```

