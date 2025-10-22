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
        Load a YAML configuration file with fallback to Python files
        
        Args:
            filename: Name of config file (without extension)
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist in any format
            yaml.YAMLError: If YAML config file is invalid
            ImportError: If Python config file cannot be imported
        """
        yaml_path = self.config_dir / f'{filename}.yaml'
        yml_path = self.config_dir / f'{filename}.yml'
        py_path = self.config_dir / f'{filename}.py'
        
        # Try .yaml first, then .yml, then .py for backward compatibility
        config_path = None
        if yaml_path.exists():
            config_path = yaml_path
        elif yml_path.exists():
            config_path = yml_path
        elif py_path.exists():
            # Fallback to Python config for backward compatibility
            import sys
            import importlib.util
            
            # Add config dir to path temporarily
            sys.path.insert(0, str(self.config_dir))
            try:
                spec = importlib.util.spec_from_file_location(filename, py_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get the config from the module
                if hasattr(module, filename):
                    return getattr(module, filename)
                else:
                    # For backward compatibility, try common variable names
                    for var_name in [filename, 'config', 'servers', 'plugins']:
                        if hasattr(module, var_name):
                            return getattr(module, var_name)
                    raise ImportError(f"Could not find config variable in {py_path}")
            finally:
                sys.path.remove(str(self.config_dir))
        else:
            raise FileNotFoundError(
                f"Config file not found: {yaml_path}, {yml_path}, or {py_path}. "
                f"Please copy example-{filename}.yaml to {filename}.yaml"
            )
        
        # Load YAML file
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
