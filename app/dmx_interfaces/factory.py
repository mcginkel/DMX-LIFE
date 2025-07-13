"""
Factory for creating DMX interface instances
"""
from flask import current_app
from .artnet import ArtNetInterface
from .usb_dmx import USBDMXInterface

class DMXInterfaceFactory:
    """Factory class for creating DMX interface instances"""
    
    INTERFACE_TYPES = {
        'artnet': ArtNetInterface,
        'usb_dmx': USBDMXInterface
    }
    
    @classmethod
    def create_interface(cls, interface_type, config):
        """Create a DMX interface instance based on type
        
        Args:
            interface_type (str): Type of interface ('artnet' or 'usb_dmx')
            config (dict): Configuration for the interface
            
        Returns:
            DMXInterface: Instance of the appropriate interface class
            
        Raises:
            ValueError: If interface_type is not supported
        """
        if interface_type not in cls.INTERFACE_TYPES:
            raise ValueError(f"Unsupported interface type: {interface_type}. "
                           f"Supported types: {list(cls.INTERFACE_TYPES.keys())}")
        
        interface_class = cls.INTERFACE_TYPES[interface_type]
        
        try:
            interface = interface_class(config)
            current_app.logger.info(f"Created {interface_type} interface")
            return interface
        except Exception as e:
            current_app.logger.error(f"Failed to create {interface_type} interface: {e}")
            raise
    
    @classmethod
    def get_available_types(cls):
        """Get list of available interface types"""
        return list(cls.INTERFACE_TYPES.keys())
    
    @classmethod
    def get_interface_info(cls):
        """Get information about available interface types"""
        return {
            'artnet': {
                'name': 'Art-Net',
                'description': 'DMX over Ethernet/WiFi using Art-Net protocol',
                'required_config': ['artnet_ip', 'universe'],
                'optional_config': ['artnet_port', 'packet_size', 'refresh_rate']
            },
            'usb_dmx': {
                'name': 'USB-DMX',
                'description': 'Direct USB connection to DMX interface',
                'required_config': [],
                'optional_config': ['usb_port', 'usb_baud_rate', 'usb_data_bits', 'usb_stop_bits', 'usb_parity', 'usb_timeout']
            }
        }
