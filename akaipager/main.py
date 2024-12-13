import mido
import fire
import numpy as np

class WildcardDict(dict):
    def __init__(self, *args, **kwargs):
        """Initialize the dictionary with an optional initial dictionary."""
        super().__init__(*args, **kwargs)

    def set(self, key, value):
        """Set a value for a given key (tuple)."""
        self[key] = value

    def get(self, key):
        """Get values for a given key with wildcards."""
        results = []
        for k, v in self.items():
            if self._matches(key, k):
                results.append(v)
        return results

    def _matches(self, query_key, store_key):
        """Check if the query_key matches the store_key with wildcards."""
        if len(query_key) != len(store_key):
            return False
        for q, s in zip(query_key, store_key):
            if s != -1 and q != s:
                return False
        return True

# Global variable to set the desired MIDI channel
GLOBAL_CHANNEL = 1  # Change this to the desired channel (0-15)

MAX_CHANNEL = 7  # Maximum MIDI channel number

# Global dictionary to set rules for MIDI messages
RULES = {
    # 'note_on': WildcardDict({
        # (-1,1): lambda op, m: note2cc(op, m, 1, 2),
    # }),
    'control_change': WildcardDict({
        (56,127,-1): lambda op, m: set_global_channel(m,0),
        (57,127,-1): lambda op, m: set_global_channel(m,1),
        (58,127,-1): lambda op, m: set_global_channel(m,2),
        (59,127,-1): lambda op, m: set_global_channel(m,3),
        (60,127,-1): lambda op, m: set_global_channel(m,4),
        (61,127,-1): lambda op, m: set_global_channel(m,5),
        (62,127,-1): lambda op, m: set_global_channel(m,6),
        (63,127,-1): lambda op, m: set_global_channel(m,7),

        (-1,-1,-1): lambda op, m: change_channel_to_global(m),
        
        # (16,-1,-1): lambda op, m: gain(m),
        # (17,-1,-1): lambda op, m: gain(m),
        # (18,-1,-1): lambda op, m: gain(m),
        # (19,-1,-1): lambda op, m: gain(m),
        # (20,-1,-1): lambda op, m: gain(m),
        # (21,-1,-1): lambda op, m: gain(m),

        (40, -1, -1): lambda op, m: mute(op,m),  # Mute function for CC 40
        (41, -1, -1): lambda op, m: mute(op,m),  # Mute function for CC 41
        (42, -1, -1): lambda op, m: mute(op,m),  # Mute function for CC 42
        (43, -1, -1): lambda op, m: mute(op,m),  # Mute function for CC 43
        (44, -1, -1): lambda op, m: mute(op,m),  # Mute function for CC 44
        (45, -1, -1): lambda op, m: mute(op,m),  # Mute function for CC 45

        (46, 127, -1): lambda op, m: create_note_on_messages(op, [60, 62, 64]),  # New rule
    })
}

mute_state = {i:False for i in range(8)}

auto = mido.open_output([x for x in mido.get_output_names() if 'MIDI Mix' in x][0])

def rec_arm_light(n, on_off):
    hex_ = 0x03 + n*3  # Calculate the hex value based on the message control
    auto.send(mido.Message.from_bytes([0x90, hex_, 0x7F if on_off else 0x00]))

def mute_light(n, on_off):
    hex_ = 0x01 + n*3  # Calculate the hex value based on the message control
    auto.send(mido.Message.from_bytes([0x90, hex_, 0x7F if on_off else 0x00]))

def mute(op, message):
    if message.value==127:
        track = (message.control-40)
        mute_state[track] = not mute_state[track]
        mute_light(track, mute_state[track])
        message.channel = 6  # Set the new channel
        message.value = 0 if mute_state[track] else 127

        return message

def create_note_on_messages(output_port, notes):
    for i,note in enumerate(notes):
        note_on_message = mido.Message('note_on', note=note, velocity=64, channel=i)  # Adjust velocity and channel as needed
        output_port.send(note_on_message)
        print(f"Sent Note On message: {note_on_message}")

def gain(message):
    # Redirect CC messages from 16 to 21 to channels 0 to 6
    message.control = message.control - 16 +1  # Map CC 16 to channel 0, CC 17 to channel 1, etc.
    message.channel = 6  # Set the new channel
    print(f"Redirecting CC {message.control+16} to channel {6} with value {message.value}")
    return message

def note2cc(output_port, message, control, channel):
    value = int(np.clip(60*2**((message.note-60)/12),0,127))  # Convert the note to a CC value
    cc_message = mido.Message('control_change', channel=channel, control=control, value=value)
    output_port.send(cc_message)  # Send the CC message
    print(f"Sent CC message: {cc_message}")

def change_channel_to_global(message):
    # only cc 0 to 7, 31 to 39, 24 to 31
    if message.control in range(8) or message.control in range(31,40) or message.control in range(24,32):    
        message.channel = GLOBAL_CHANNEL  # Set to the global channel
        print(f"Changed channel to {GLOBAL_CHANNEL}")
        return message

def set_global_channel(message, channel):
    if message.value == 127:
        # Turn off all rec arm light
        for i in range(8):
            rec_arm_light(i, False)
        rec_arm_light(message.control-56, True)

        global GLOBAL_CHANNEL
        if 0 <= channel <= MAX_CHANNEL:
            GLOBAL_CHANNEL = channel  # Set to the specified channel
        print(f"Global channel set to {GLOBAL_CHANNEL}")

class MidiPortSelector:
    def __init__(self):
        self.input_ports = mido.get_input_names()
        self.output_ports = mido.get_output_names()

    def list_ports(self):
        print("Available MIDI Input Ports:")
        for i, port in enumerate(self.input_ports):
            print(f"{i}: {port}")
        
        print("\nAvailable MIDI Output Ports:")
        for i, port in enumerate(self.output_ports):
            print(f"{i}: {port}")

    def select_ports(self, input_index: int, output_index: int):
        # New method to find port index by name
        def find_port_index(port_list, name):
            for i, port in enumerate(port_list):
                if name in port:
                    return i
            return None 

        # Check if input_index is a string and find the index
        if isinstance(input_index, str):
            input_index = find_port_index(self.input_ports, input_index)
        
        # Check if output_index is a string and find the index
        if isinstance(output_index, str):
            output_index = find_port_index(self.output_ports, output_index)
        
        if input_index is None or output_index is None:
            print("Port not found.")
            print ("Available MIDI Input Ports:")
            for i, port in enumerate(self.input_ports):
                print(f"{i}: {port}")
            print("\nAvailable MIDI Output Ports:")
            for i, port in enumerate(self.output_ports):
                print(f"{i}: {port}")
            return  

        print(f"Selected Input Port: {self.input_ports[input_index]}")
        print(f"Selected Output Port: {self.output_ports[output_index]}")

        if input_index < 0 or input_index >= len(self.input_ports):
            print("Invalid input port index.")
            return
        if output_index < 0 or output_index >= len(self.output_ports):
            print("Invalid output port index.")
            return

        input_port = mido.open_input(self.input_ports[input_index])
        output_port = mido.open_output(self.output_ports[output_index])

        try:
            print("Redirecting MIDI messages...")
            for message in input_port:
                # Check for rules based on message type and note
                called = False

                if message.type in RULES:
                    if message.type == 'note_on' or message.type == 'note_off':
                        print(message)
                        calls = RULES[message.type].get((message.note, message.channel))  # Run the associated function
                        
                    else:                                               
                        calls = RULES[message.type].get((message.control, message.value, message.channel))  # Run the associated function
                    for call in calls:
                        output = call(output_port, message)
                        if isinstance(output, mido.Message):
                            message = output
                        print(message)
                        # called = True
                        
                # Change the channel of the message
                # if not called and message.type in ['note_on', 'note_off', 'control_change']:
                #     message.channel = GLOBAL_CHANNEL  # Set to the global channel

                output_port.send(message)  # Send the modified message to the output port
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            input_port.close()
            output_port.close()

if __name__ == '__main__':
    fire.Fire(MidiPortSelector)