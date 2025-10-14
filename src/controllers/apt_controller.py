from models.package_model import Package

class APTController:
    def __init__(self):
        pass

    def install_package(self, package_name):
        # Placeholder for APT install
        return True

    def remove_package(self, package_name):
        # Placeholder for APT remove
        return True

    def search_packages(self, query):
        # Mock search results
        return [
            Package(f"package-{query}-1", "1.0", f"Sample package matching {query}"),
            Package(f"package-{query}-2", "2.0", f"Another package for {query}")
        ]

    def get_installed_packages(self):
        # Mock installed packages
        return [
            Package("firefox", "100.0", "Web browser"),
            Package("vim", "8.2", "Text editor"),
            Package("git", "2.34", "Version control")
        ]