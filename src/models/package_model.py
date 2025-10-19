class Package:
    def __init__(self, name, version, description, backend="apt"):
        self.name = name
        self.version = version
        self.description = description
        self.backend = backend.lower()  # Normalize to lowercase

    def __str__(self):
        return f"{self.name} - {self.version}: {self.description} [{self.backend.upper()}]"