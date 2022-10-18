import pygame

class Music():
    def __init__(self):
        melody = 'arcada.ogg'
        self.sound_good = pygame.mixer.Sound('fire1.ogg') 
        self.sound_evil = pygame.mixer.Sound('fire2.ogg') 
        self.sound_good.set_volume(0.2)
        self.sound_evil.set_volume(0.2) 

        pygame.mixer.music.load(melody)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        self.is_playing = True
    
    def good_fire(self):
        if self.is_playing:
            self.sound_good.play()

    def evil_fire(self):
        if self.is_playing:
            self.sound_evil.play()

    def change(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def volume_up(self):
        v = min(1, pygame.mixer.music.get_volume() + 0.1)
        pygame.mixer.music.set_volume(v)

    def volume_down(self):
        v = max(0, pygame.mixer.music.get_volume() - 0.1)
        pygame.mixer.music.set_volume(v)

