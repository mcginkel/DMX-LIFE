"""
Models for DMX fixtures and scenes
"""

from flask.cli import F


class Fixture:
    """Represents a DMX fixture"""
    
    def __init__(self, name, fixture_type, start_channel, channel_count):
        self.name = name
        self.fixture_type = fixture_type
        self.start_channel = start_channel
        self.channel_count = channel_count
        
    def to_dict(self):
        """Convert fixture to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'type': self.fixture_type,
            'start_channel': self.start_channel,
            'channel_count': self.channel_count
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create fixture from dictionary"""
        return cls(
            data.get('name', 'Unknown'),
            data.get('type', 'Generic'),
            data.get('start_channel', 1),
            data.get('channel_count', 1)
        )


class FixtureType:
    """Represents a type of DMX fixture with channel definitions"""
    
    # Common fixture types
    TYPES = {
        'Generic': {
            'channels': [
                {'name': 'Dimmer', 'default': 0, 'visible': True}
            ]
        },
        'RGB': {
            'channels': [
                {'name': 'Red', 'default': 0, 'visible': True},
                {'name': 'Green', 'default': 0, 'visible': True},
                {'name': 'Blue', 'default': 0, 'visible': True}
            ]
        },
        'ShowTec LEDPAR 56': {
            'channels': [
                {'name': 'Red', 'default': 0, 'visible': True},
                {'name': 'Green', 'default': 0, 'visible': True},
                {'name': 'Blue', 'default': 0, 'visible': True},
                {'name': 'Full Color', 'default': 0, 'visible': False},
                {'name': 'Strobe en Speed', 'default': 0, 'visible': False},
                {'name': 'Modi', 'default': 0, 'visible': False}
            ]
        },
        'Performer 2000 - 13ch tour': {
            'channels': [
                {'name': 'dimmer', 'default': 0, 'visible': True},
                {'name': 'Rood', 'default': 0, 'visible': True},
                {'name': 'Groen', 'default': 0, 'visible': True},
                {'name': 'Blauw', 'default': 0, 'visible': True},
                {'name': 'Amber', 'default': 0, 'visible': True},
                {'name': 'Limoen', 'default': 0, 'visible': True},
                {'name': 'Kleurvoorinstelling', 'default': 0, 'visible': True},
                {'name': 'Macro', 'default': 0, 'visible': False},
                {'name': 'Stroboscoop', 'default': 0, 'visible': False},
                {'name': 'Zoom kl->gr', 'default': 0, 'visible': True},
                {'name': 'Programma', 'default': 0, 'visible': False},
                {'name': 'Programmasnelheid', 'default': 0, 'visible': False},
                {'name': 'Dimmersnelheid', 'default': 0, 'visible': False}
            ]
        },
        'Compac Par 18 Tri': {
            'channels': [
                {'name': 'Dimmer', 'default': 0, 'visible': True},
                {'name': 'Rood', 'default': 0, 'visible': True},
                {'name': 'Groen', 'default': 0, 'visible': True},
                {'name': 'Blauw', 'default': 0, 'visible': True}
            ]
        },
    }
    
    @classmethod
    def get_types(cls):
        """Get available fixture types"""
        return list(cls.TYPES.keys())
    
    @classmethod
    def get_channels(cls, fixture_type):
        """Get channels for a fixture type"""
        if fixture_type in cls.TYPES:
            return cls.TYPES[fixture_type]['channels']
        return cls.TYPES['Generic']['channels']
