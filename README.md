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
For full documentation, please visit our [dedicated]() site.

## Setup
All operations are available through the `ArmisSdk` class.
The simplest way to initialise it is by populating the following environment variables:
* `ARMIS_TENANT`: The name of the Armis tenant you're working with.
* `ARMIS_SECRET_KEY`: The secret key you got from the tenant and will be used to authenticate requests.
* `ARMIS_CLIENT_ID`: The unique identifier of your app.

and then:
```python
from armis_sdk import ArmisSdk

ArmisSdk()
```
Alternatively, you can pass the values directly:
```python
from armis_sdk import ArmisSdk

ArmisSdk(
    tenant="<my_tenant>", 
    secret_key="<my_secret_key>",
    client_id="<my_client_id>",
)
```

## Asynchronous code
All method in the SDK are asynchronous unless specified otherwise.
For example, if you wish to iterate over all sites in your tenant, you should:
```python
import asyncio
from armis_sdk import ArmisSdk

async def main():
    armis_sdk = ArmisSdk()
    async for site in await armis_sdk.sites.list():
        print(site)

asyncio.run(main())
```

