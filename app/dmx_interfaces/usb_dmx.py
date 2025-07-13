"""
USB-DMX Interface Implementation
"""
import time
import threading
from flask import current_app
from .base import DMXInterface

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class USBDMXInterface(DMXInterface):
    """USB-DMX implementation of DMX interface"""
    
    # Common USB-DMX device identifiers
    KNOWN_DEVICES = [
        {'vid': 0x0403, 'pid': 0x6001, 'name': 'FTDI USB-DMX'},  # Generic FTDI
        {'vid': 0x16C0, 'pid': 0x05DC, 'name': 'Enttec Open DMX'},  # Enttec Open DMX
        {'vid': 0x0403, 'pid': 0x6015, 'name': 'DMXking ultraDMX'},  # DMXking
    ]
    
    def __init__(self, config):
        super().__init__(config)
        self.serial_port = None
        self.port_name = config.get('usb_port', 'auto')
        self.baud_rate = config.get('usb_baud_rate', 250000)  # Standard DMX baud rate
        self.data_bits = config.get('usb_data_bits', 8)
        self.stop_bits = config.get('usb_stop_bits', 2)
        self.parity = config.get('usb_parity', 'N')
        self.timeout = config.get('usb_timeout', 1.0)
        self.send_lock = threading.Lock()
        
    def start(self):
        """Start the USB-DMX interface"""
        if not SERIAL_AVAILABLE:
            current_app.logger.error("PySerial not available. Install with: pip install pyserial")
            return False
            
        try:
            # Auto-detect port if needed
            if self.port_name == 'auto':
                self.port_name = self._auto_detect_port()
                if not self.port_name:
                    current_app.logger.error("No USB-DMX device found")
                    return False
                    
            # Open serial connection
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baud_rate,
                bytesize=self.data_bits,
                stopbits=self.stop_bits,
                parity=self.parity,
                timeout=self.timeout
            )
            
            self.is_started = True
            current_app.logger.info(f"USB-DMX interface started on {self.port_name}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to start USB-DMX interface: {e}")
            return False
            
    def stop(self):
        """Stop the USB-DMX interface"""
        if self.serial_port and self.is_started:
            try:
                self.serial_port.close()
                self.is_started = False
                current_app.logger.info("USB-DMX interface stopped")
                return True
            except Exception as e:
                current_app.logger.error(f"Error stopping USB-DMX interface: {e}")
                return False
        return True
        
    def send_dmx(self, dmx_data):
        """Send DMX data via USB"""
        if not self.serial_port or not self.is_started:
            return False
            
        try:
            with self.send_lock:
                # DMX512 packet structure for Enttec Open DMX USB
                # Start of packet
                packet = bytearray([0x7E])  # Start delimiter
                packet.append(6)  # Label: Send DMX packet request
                packet.append(513 & 0xFF)  # Data length LSB (513 = 1 start code + 512 channels)
                packet.append((513 >> 8) & 0xFF)  # Data length MSB
                packet.append(0)  # DMX start code
                packet.extend(dmx_data[:512])  # DMX data (ensure max 512 channels)
                packet.append(0xE7)  # End delimiter
                
                self.serial_port.write(packet)
                self.serial_port.flush()
                return True
                
        except Exception as e:
            current_app.logger.error(f"Error sending USB-DMX data: {e}")
            return False
            
    def is_available(self):
        """Check if USB-DMX device is available"""
        try:
            if not SERIAL_AVAILABLE:
                return False
                
            if self.port_name == 'auto':
                return len(self.get_available_ports()) > 0
            else:
                # Check if specific port exists
                available_ports = [port.device for port in serial.tools.list_ports.comports()]
                return self.port_name in available_ports
                
        except Exception:
            return False
            
    def get_status(self):
        """Get USB-DMX interface status"""
        return {
            'type': 'usb_dmx',
            'port': self.port_name,
            'baud_rate': self.baud_rate,
            'is_started': self.is_started,
            'is_available': self.is_available(),
            'available_ports': self.get_available_ports()
        }
        
    def get_available_ports(self):
        """Get list of available USB-DMX ports"""
        if not SERIAL_AVAILABLE:
            return []
            
        try:
            ports = []
            for port in serial.tools.list_ports.comports():
                port_info = {
                    'device': port.device,
                    'description': port.description,
                    'vid': getattr(port, 'vid', None),
                    'pid': getattr(port, 'pid', None),
                    'is_dmx_device': self._is_known_dmx_device(port)
                }
                ports.append(port_info)
            return ports
        except Exception as e:
            current_app.logger.error(f"Error listing USB ports: {e}")
            return []
            
    def _auto_detect_port(self):
        """Auto-detect USB-DMX device port"""
        try:
            for port in serial.tools.list_ports.comports():
                if self._is_known_dmx_device(port):
                    current_app.logger.info(f"Auto-detected USB-DMX device: {port.device} ({port.description})")
                    return port.device
                    
            # If no known device found, try any USB-serial device
            for port in serial.tools.list_ports.comports():
                if 'USB' in port.description.upper() or 'SERIAL' in port.description.upper():
                    current_app.logger.warning(f"Using potential USB-DMX device: {port.device} ({port.description})")
                    return port.device
                    
        except Exception as e:
            current_app.logger.error(f"Error auto-detecting USB-DMX port: {e}")
            
        return None
        
    def _is_known_dmx_device(self, port):
        """Check if port matches known DMX device"""
        vid = getattr(port, 'vid', None)
        pid = getattr(port, 'pid', None)
        
        if vid and pid:
            for device in self.KNOWN_DEVICES:
                if device['vid'] == vid and device['pid'] == pid:
                    return True
                    
        # Also check description for known terms
        description = port.description.upper()
        dmx_terms = ['DMX', 'ENTTEC', 'FTDI', 'DMXKING']
        return any(term in description for term in dmx_terms)
        
    def update_config(self, new_config):
        """Update USB-DMX configuration"""
        super().update_config(new_config)
        
        # Update instance variables
        self.port_name = self.config.get('usb_port', 'auto')
        self.baud_rate = self.config.get('usb_baud_rate', 250000)
        self.data_bits = self.config.get('usb_data_bits', 8)
        self.stop_bits = self.config.get('usb_stop_bits', 2)
        self.parity = self.config.get('usb_parity', 'N')
        self.timeout = self.config.get('usb_timeout', 1.0)
        
        # Restart if currently running
        if self.is_started:
            self.stop()
            time.sleep(0.1)  # Brief pause
            self.start()
