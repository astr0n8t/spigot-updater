"""
Configuration loader utility for YAML config files
"""
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Load configuration from YAML files with fallback to Python files"""
    
    def __init__(self, config_dir: Path = None):
        """
        Initialize config loader
        
        Args:
            config_dir: Path to config directory. Defaults to ../config from this file.
        """
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent.parent / 'config'
        else:
            self.config_dir = Path(config_dir)
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file
        
        Args:
            filename: Name of YAML file (without extension)
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        yaml_path = self.config_dir / f'{filename}.yaml'
        yml_path = self.config_dir / f'{filename}.yml'
        
        # Try .yaml first, then .yml
        config_path = None
        if yaml_path.exists():
            config_path = yaml_path
        elif yml_path.exists():
            config_path = yml_path
        else:
            raise FileNotFoundError(
                f"Config file not found: {yaml_path} or {yml_path}. "
                f"Please copy example-{filename}.yaml to {filename}.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            return {}
        
        return config
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load main configuration
        
        Returns:
            Dictionary containing main config
        """
        config = self.load_yaml('config')
        
        # For backwards compatibility, add DEBUG and SAVE_LOGS
        config['DEBUG'] = config.get('debug', False)
        config['SAVE_LOGS'] = config.get('save_logs', True)
        
        return config
    
    def load_servers(self) -> Dict[str, Any]:
        """
        Load servers configuration
        
        Returns:
            Dictionary containing server configs
        """
        return self.load_yaml('servers')
    
    def load_plugins(self) -> Dict[str, Any]:
        """
        Load plugins configuration
        
        Returns:
            Dictionary containing plugin configs
        """
        return self.load_yaml('plugins')
    
    def load_all(self) -> Dict[str, Any]:
        """
        Load all configuration files
        
        Returns:
            Dictionary containing all configs merged
        """
        config = self.load_config()
        config['servers'] = self.load_servers()
        config['plugins'] = self.load_plugins()
        
        return config
