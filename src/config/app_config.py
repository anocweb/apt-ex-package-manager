import argparse
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration from command-line arguments"""
    dev_outline: bool
    dev_logging: bool
    stdout_log_level: str
    show_updates: bool
    
    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'AppConfig':
        """Create config from parsed arguments"""
        return cls(
            dev_outline=args.dev_outline,
            dev_logging=args.dev_logging,
            stdout_log_level=args.stdout_log_level,
            show_updates=args.show_updates
        )
    
    @classmethod
    def parse_arguments(cls) -> 'AppConfig':
        """Parse command-line arguments and return config"""
        parser = argparse.ArgumentParser(description='Apt-Ex Package Manager')
        parser.add_argument('--dev-outline', action='store_true', 
                          help='Enable development widget outlines')
        parser.add_argument('--dev-logging', action='store_true', 
                          help='Automatically open logging window')
        parser.add_argument('--stdout-log-level', default='WARNING', 
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                          help='Maximum log level to show on stdout (default: WARNING)')
        parser.add_argument('--show-updates', action='store_true',
                          help='Open directly to updates page')
        args = parser.parse_args()
        return cls.from_args(args)
