from armis_sdk.core.base_entity import BaseEntity


class AssetFieldDescription(BaseEntity):
    name: str
    type: str
    is_list: bool = False
