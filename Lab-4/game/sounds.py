"""Procedurally generated sound effects (no audio files needed)."""
import math
import random
from array import array

import pygame

SAMPLE_RATE = 44100


def _make(samples):
    # Duplicate each sample per channel so it matches however the mixer was opened
    channels = pygame.mixer.get_init()[2]
    interleaved = [v for v in samples for _ in range(channels)]
    return pygame.mixer.Sound(buffer=array("h", interleaved).tobytes())


def _shoot():
    n = int(SAMPLE_RATE * 0.12)
    out = []
    for i in range(n):
        t = i / n
        freq = 900 - 600 * t  # falling "pew"
        out.append(int(9000 * (1 - t) * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)))
    return _make(out)


def _explosion():
    n = int(SAMPLE_RATE * 0.25)
    out = []
    for i in range(n):
        t = i / n
        out.append(int(12000 * (1 - t) ** 2 * random.uniform(-1, 1)))
    return _make(out)


def _game_over():
    out = []
    for freq, dur in ((440, 0.18), (370, 0.18), (294, 0.18), (196, 0.45)):
        n = int(SAMPLE_RATE * dur)
        for i in range(n):
            env = 1 - i / n
            out.append(int(9000 * env * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)))
    return _make(out)


class Sounds:
    """Safe wrapper: if no audio device is available the game still runs silently."""

    def __init__(self):
        self.enabled = False
        self.shoot = self.explosion = self.game_over = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
            fmt = pygame.mixer.get_init()
            if fmt and fmt[1] == -16:
                self.shoot, self.explosion, self.game_over = _shoot(), _explosion(), _game_over()
                self.enabled = True
        except pygame.error:
            self.enabled = False

    def play(self, name):
        if self.enabled:
            getattr(self, name).play()
