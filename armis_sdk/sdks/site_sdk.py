from typing import List, AsyncIterator


from armis_sdk.core.base_sdk import BaseSdk
from armis_sdk.entities.site import Site


class SitesSdk(BaseSdk):

    async def hierarchy(self) -> List[Site]:
        id_to_site = {site.id: site async for site in await self.list()}
        root = []
        for site in id_to_site.values():
            if parent := id_to_site.get(site.parent_id):
                parent.children.append(site)
            else:
                root.append(site)

        return root

    async def list(self) -> AsyncIterator[Site]:
        return self._paginate("/api/v1/sites/", "sites", Site)
