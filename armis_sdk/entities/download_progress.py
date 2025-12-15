from armis_sdk.core.base_entity import BaseEntity


class DownloadProgress(BaseEntity):
    downloaded: int
    """How much bytes were already downloaded."""

    total: int
    """Total number of bytes to download."""

    @property
    def percent(self) -> str:
        """Percentage of progress."""
        return f"{self.downloaded/self.total:.4%}"
