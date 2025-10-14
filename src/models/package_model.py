class Package:
    def __init__(self, name, version, description, backend="APT"):
        self.name = name
        self.version = version
        self.description = description
        self.backend = backend

    def __str__(self):
        return f"{self.name} - {self.version}: {self.description}"