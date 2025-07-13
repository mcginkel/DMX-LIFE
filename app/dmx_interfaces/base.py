"""
Abstract base class for DMX interfaces
"""
from abc import ABC, abstractmethod

class DMXInterface(ABC):
    """Abstract base class for all DMX interface implementations"""
    
    def __init__(self, config):
        """Initialize the DMX interface with configuration"""
        self.config = config
        self.is_started = False
        
    @abstractmethod
    def start(self):
        """Start the DMX interface"""
        pass
        
    @abstractmethod
    def stop(self):
        """Stop the DMX interface"""
        pass
        
    @abstractmethod
    def send_dmx(self, dmx_data):
        """Send DMX data (512 bytes)"""
        pass
        
    @abstractmethod
    def is_available(self):
        """Check if the interface is available/reachable"""
        pass
        
    @abstractmethod
    def get_status(self):
        """Get status information about the interface"""
        pass
        
    def get_config(self):
        """Get the current configuration"""
        return self.config.copy()
        
    def update_config(self, new_config):
        """Update the configuration"""
        self.config.update(new_config)
