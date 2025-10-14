class PackageModel:
    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    def fetch_package_info(self):
        # Logic to fetch package information from APT
        pass

    def update_package_info(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description
        # Logic to update package information in APT
        pass

    def __str__(self):
        return f"{self.name} - {self.version}: {self.description}"