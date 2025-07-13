"""
Art-Net DMX Interface Implementation
"""
import time
from flask import current_app
from stupidArtnet import StupidArtnet
from .ping import ping_simple
from .base import DMXInterface

class ArtNetInterface(DMXInterface):
    """Art-Net implementation of DMX interface"""
    
    def __init__(self, config):
        super().__init__(config)
        self.artnet = None
        self.target_ip = config.get('artnet_ip', '255.255.255.255')
        self.universe = config.get('universe', 0)
        self.packet_size = config.get('packet_size', 512)
        self.refresh_rate = config.get('refresh_rate', 30)
        
    def start(self):
        """Start the Art-Net interface"""
        try:
            self.artnet = StupidArtnet(
                self.target_ip,
                self.universe,
                self.packet_size,
                self.refresh_rate
            )
            self.artnet.set_simplified(False)
            self.artnet.set_net(0)
            self.artnet.set_subnet(0)
            self.artnet.start()
            self.is_started = True
            current_app.logger.info(f"Art-Net interface started: {self.target_ip}:{self.universe}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to start Art-Net interface: {e}")
            return False
            
    def stop(self):
        """Stop the Art-Net interface"""
        if self.artnet and self.is_started:
            try:
                self.artnet.stop()
                self.is_started = False
                current_app.logger.info("Art-Net interface stopped")
                return True
            except Exception as e:
                current_app.logger.error(f"Error stopping Art-Net interface: {e}")
                return False
        return True
        
    def send_dmx(self, dmx_data):
        """Send DMX data via Art-Net"""
        if not self.artnet or not self.is_started:
            return False
            
        try:
            self.artnet.set(dmx_data)
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending Art-Net data: {e}")
            return False
            
    def is_available(self):
        """Check if Art-Net target is reachable"""
        try:
            # Don't ping broadcast addresses
            if self.target_ip == '255.255.255.255':
                return True
            return ping_simple(self.target_ip)
        except Exception:
            return False
            
    def get_status(self):
        """Get Art-Net interface status"""
        return {
            'type': 'artnet',
            'target_ip': self.target_ip,
            'universe': self.universe,
            'is_started': self.is_started,
            'is_available': self.is_available()
        }
        
    def update_config(self, new_config):
        """Update Art-Net configuration"""
        super().update_config(new_config)
        
        # Update instance variables
        self.target_ip = self.config.get('artnet_ip', '255.255.255.255')
        self.universe = self.config.get('universe', 0)
        self.packet_size = self.config.get('packet_size', 512)
        self.refresh_rate = self.config.get('refresh_rate', 30)
        
        # Restart if currently running
        if self.is_started:
            self.stop()
            time.sleep(0.1)  # Brief pause
            self.start()
