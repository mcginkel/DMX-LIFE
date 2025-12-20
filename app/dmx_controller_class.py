"""
DMX Controller - Handles DMX hardware communication and smooth transitions
"""
import time
import threading
import socket
from flask import current_app
from stupidArtnet import StupidArtnet


class DMXController:
    """Manages DMX hardware output via Art-Net with smooth transitions"""
    
    TRANSITION_DURATION = 3.0  # Transition duration in seconds
    UPDATE_RATE = 0.033  # ~30fps update rate
    
    def __init__(self, artnet_ip, universe, packet_size, refresh_rate):
        """
        Initialize DMX controller
        
        Args:
            artnet_ip: IP address for Art-Net output
            universe: DMX universe number
            packet_size: Number of DMX channels (typically 512)
            refresh_rate: FPS for DMX output
        """
        self.artnet = StupidArtnet(artnet_ip, universe, packet_size, refresh_rate)
        self.artnet.set_simplified(False)
        self.artnet.set_net(0)
        self.artnet.set_subnet(0)
        
        # DMX value buffers
        self.current_values = bytearray(512)
        self.target_values = bytearray(512)
        
        # Transition state
        self.transition_active = False
        self.transition_start_time = 0
        
        # Thread control
        self._thread = None
        self._running = False
        
        # Connection status tracking
        self.connection_status = {
            'connected': True,
            'last_error_time': 0,
            'error_message': None
        }
    
    def _send_dmx_packet(self, buffer):
        """
        Send DMX packet with connection status tracking
        
        Args:
            buffer: bytearray(512) with DMX values
        """
        packet = bytearray()
        packet.extend(self.artnet.packet_header)
        packet.extend(buffer)
        
        try:
            self.artnet.socket_client.sendto(packet, (self.artnet.target_ip, self.artnet.port))
            
            # Send artsync if enabled (suppress errors)
            if self.artnet.if_sync:
                try:
                    self.artnet.make_artsync_header()
                    self.artnet.socket_client.sendto(
                        self.artnet.artsync_header, 
                        (self.artnet.target_ip, self.artnet.port)
                    )
                except socket.error:
                    pass  # Silently ignore artsync errors
            
            # Update connection status on successful send
            if not self.connection_status['connected']:
                self.connection_status['connected'] = True
                self.connection_status['error_message'] = None
                if current_app:
                    current_app.logger.info("Art-Net connection restored")
                    
        except socket.error as error:
            current_time = time.time()
            
            # Update connection status
            was_connected = self.connection_status['connected']
            self.connection_status['connected'] = False
            self.connection_status['last_error_time'] = current_time
            self.connection_status['error_message'] = str(error)
            
            # Only log once when connection is first lost (not repeatedly)
            if was_connected:
                if current_app:
                    current_app.logger.warning(f"Art-Net connection lost: {error}")
        finally:
            self.artnet.sequence = (self.artnet.sequence + 1) % 256
    
    def start(self):
        """Start the DMX output thread"""
        if self._thread is not None:
            return
        
        self._running = True
        # Note: We don't call self.artnet.start() because it starts its own thread
        # and calls show() which prints errors. We manage our own thread instead.
        
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        if current_app:
            current_app.logger.info("DMX controller thread started")
    
    def stop(self):
        """Stop the DMX output thread"""
        if self._thread is None:
            return
        
        self._running = False
        # Note: We don't call self.artnet.stop() because we manage our own thread
        
        self._thread.join(timeout=2.0)
        self._thread = None
        
        if current_app:
            current_app.logger.info("DMX controller thread stopped")
    
    def _run(self):
        """Main thread loop - handles smooth transitions and DMX output"""
        while self._running:
            time.sleep(self.UPDATE_RATE)
            
            if self.transition_active:
                self._update_transition()
            
            # Always send DMX values (for connection monitoring)
            self._send_dmx_packet(self.current_values)
    
    def _update_transition(self):
        """Update DMX values during a transition"""
        # Calculate progress (0.0 to 1.0)
        elapsed = time.time() - self.transition_start_time
        progress = min(elapsed / self.TRANSITION_DURATION, 1.0)
        
        # Interpolate all channels
        for i in range(512):
            if self.current_values[i] != self.target_values[i]:
                current = self.current_values[i]
                target = self.target_values[i]
                interpolated = int(current + (target - current) * progress)
                self.current_values[i] = interpolated
        
        # Check if transition is complete
        if progress >= 1.0:
            self.transition_active = False
            # Ensure final values match targets exactly
            for i in range(512):
                self.current_values[i] = self.target_values[i]
    
    def set_with_transition(self, buffer):
        """
        Set DMX values with smooth transition
        
        Args:
            buffer: bytearray(512) with target DMX values
        """
        if not isinstance(buffer, bytearray) or len(buffer) != 512:
            raise ValueError("Buffer must be bytearray of length 512")
        
        # Update target values
        for i in range(512):
            self.target_values[i] = buffer[i]
        
        # Start transition
        self.transition_active = True
        self.transition_start_time = time.time()
    
    def set_immediate(self, buffer):
        """
        Set DMX values immediately without transition (for testing)
        
        Args:
            buffer: bytearray(512) with DMX values
        """
        if not isinstance(buffer, bytearray) or len(buffer) != 512:
            raise ValueError("Buffer must be bytearray of length 512")
        
        # Update both current and target
        for i in range(512):
            self.current_values[i] = buffer[i]
            self.target_values[i] = buffer[i]
        
        # Cancel any active transition
        self.transition_active = False
        
        # Send immediately
        self._send_dmx_packet(buffer)
    
    def get_current_values(self):
        """Get current DMX values (for monitoring)"""
        return self.current_values
    
    def get_connection_status(self):
        """Get connection status (for monitoring)"""
        return self.connection_status.copy()
    
    def reconfigure(self, artnet_ip=None, universe=None, packet_size=None, refresh_rate=None):
        """
        Reconfigure the Art-Net connection
        
        Args:
            artnet_ip: New IP address (optional)
            universe: New universe (optional)
            packet_size: New packet size (optional)
            refresh_rate: New refresh rate (optional)
        """
        # Stop current instance
        was_running = self._running
        if was_running:
            self.stop()
        
        # Get current settings if not provided
        if artnet_ip is None:
            artnet_ip = self.artnet.target_ip
        if universe is None:
            universe = self.artnet.universe
        if packet_size is None:
            packet_size = self.artnet.packet_size
        if refresh_rate is None:
            refresh_rate = self.artnet.fps
        
        # Reinitialize Art-Net
        self.artnet = StupidArtnet(artnet_ip, universe, packet_size, refresh_rate)
        self.artnet.set_simplified(False)
        self.artnet.set_net(0)
        self.artnet.set_subnet(0)
        
        # Restart if it was running
        if was_running:
            self.start()
        
        if current_app:
            current_app.logger.info(f"DMX controller reconfigured: {artnet_ip}, universe {universe}")
