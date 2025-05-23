"""
Models for DMX fixtures and scenes
"""

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
                {'name': 'Dimmer', 'default': 0}
            ]
        },
        'RGB': {
            'channels': [
                {'name': 'Red', 'default': 0},
                {'name': 'Green', 'default': 0},
                {'name': 'Blue', 'default': 0}
            ]
        },
        'RGBW': {
            'channels': [
                {'name': 'Red', 'default': 0},
                {'name': 'Green', 'default': 0},
                {'name': 'Blue', 'default': 0},
                {'name': 'White', 'default': 0}
            ]
        },
        'Moving Head': {
            'channels': [
                {'name': 'Pan', 'default': 128},
                {'name': 'Tilt', 'default': 128},
                {'name': 'Pan Fine', 'default': 0},
                {'name': 'Tilt Fine', 'default': 0},
                {'name': 'Speed', 'default': 0},
                {'name': 'Dimmer', 'default': 0},
                {'name': 'Red', 'default': 0},
                {'name': 'Green', 'default': 0},
                {'name': 'Blue', 'default': 0},
                {'name': 'White', 'default': 0},
                {'name': 'Gobo', 'default': 0},
                {'name': 'Gobo Rotation', 'default': 0},
                {'name': 'Color', 'default': 0},
                {'name': 'Prism', 'default': 0}
            ]
        }
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
