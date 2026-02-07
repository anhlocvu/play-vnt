import ctypes
from sound_lib import output, stream

o = output.Output()  # I fucking hate globals, and I hate you for using them, but


# this is easy so violence begets violence or something
class SoundCacher:
    def __init__(self):
        self.cache = {}
        self.refs = []  # so sound objects don't get eaten by the gc

    def play(self, file_name, pan=0.0, volume=1.0, pitch=1.0):
        if file_name not in self.cache:
            with open(file_name, "rb") as f:
                self.cache[file_name] = ctypes.create_string_buffer(f.read())
        sound = stream.FileStream(
            mem=True, file=self.cache[file_name], length=len(self.cache[file_name])
        )
        if pan:
            sound.pan = pan
        if volume != 1.0:
            sound.volume = volume
        if pitch != 1.0:
            sound.set_frequency(int(sound.get_frequency() * pitch))
        sound.play()
        self.refs.append(sound)

        # Fix memory leak: remove sound from refs when it's done playing
        def on_finished(handle, channel, data, user):
            if sound in self.refs:
                self.refs.remove(sound)

        # We need to register this callback with BASS via sound_lib stream
        try:
            from sound_lib.external.pybass import BASS_ChannelSetSync, BASS_SYNC_END, SYNCPROC
            # Keep a reference to the callback to prevent GC
            sound._finished_callback = SYNCPROC(on_finished)
            BASS_ChannelSetSync(sound.handle, BASS_SYNC_END, 0, sound._finished_callback, None)
        except Exception:
            pass

        return sound
