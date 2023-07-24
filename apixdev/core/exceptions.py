class DownloadError(Exception):
    """Exception raised for download errors."""

    def __init__(self, filename, url, http_code):
        self.filename = filename
        self.url = url
        self.http_code = http_code
        self.message = (
            f"Error while trying to download {filename} from {url} (HTTP {http_code})."
        )
        super().__init__(self.message)


class NoContainerFound(Exception):
    """Exception raised for Docker containers errors."""

    def __init__(self, name):
        self.name = name
        self.message = f"No container found for {name}."
        super().__init__(self.message)


class ExternalDependenciesMissing(Exception):
    """Exception raised for system package missing ."""

    def __init__(self, name):
        self.name = name
        self.message = f"System package missing, please install {name} first."
        super().__init__(self.message)
