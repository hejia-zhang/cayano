import Leap, sys
import pygame
import winsound
import time
import multiprocessing
import os.path as osp
import threading
import math


BLACK_HEIGHT = 300
BLACK_WIDTH = 50
WHITE_HEIGHT = 500
WHITE_WIDTH = 100

# creating the event
KEYTAP = pygame.USEREVENT + 1
KEYDRAWFINGERS = pygame.USEREVENT + 2

FREQUENCY = [261, 277, 293, 311, 330, 349, 370, 392, 415, 440, 466, 494, 523, 554, 587, 622, 659, 699, 740, 784, 830, 880, 932, 988]

class Keyboard:
    keys = []
    def __init__(self, keys):
        for key in keys:
            self.keys.append(key)

    def press(self, key):
        # beep, change color, change color back
        key.changeColor([128, 128, 128])
        key.beep()

    def determineKeyPressed(self, xTap, yTap):
        black_arr = [1,3,6,8,10,13,15,18,20,22]
        if yTap <= BLACK_HEIGHT:
            for i in range(len(self.keys)):
                if xTap >= self.keys[i].left_top_pos[0] and xTap <= self.keys[i].left_top_pos[0] + BLACK_WIDTH and i in black_arr:
                    return self.keys[i]

        for i in range(len(self.keys)):
            if xTap >= self.keys[i].left_top_pos[0] and xTap <= self.keys[i].left_top_pos[0] + WHITE_WIDTH and i not in black_arr:
                return self.keys[i]

class Key:
    frequency = 0
    duration = 0
    color = (0, 0, 0)
    kind = "white"
    left_top_pos = [0, 0]
    image = pygame.Surface((WHITE_WIDTH, WHITE_HEIGHT))
    state_lock = threading.Lock()
    timer = None

    def __init__(self, frequency, duration, kind, left_top_pos, sound_path, channel):
        self.frequency = frequency
        self.duration = duration
        self.kind = kind
        # self.timer = threading.Timer(2, self.turnColorBack())
        if (self.kind == "white"):
            self.color = (255, 255, 255)
            self.width = WHITE_WIDTH
            self.height = WHITE_HEIGHT

            self.image = pygame.Surface((WHITE_WIDTH, WHITE_HEIGHT))
            self.image.fill((255, 255, 255))
        else:
            self.color = (0, 0, 0)
            self.width = BLACK_WIDTH
            self.height = BLACK_HEIGHT

            self.image = pygame.Surface((BLACK_WIDTH, BLACK_HEIGHT))
            self.image.fill((0, 0, 0))

        self.left_top_pos = left_top_pos
        self.channel = channel
        self.sound = pygame.mixer.Sound(sound_path)

    def beep(self):
        if not self.channel.get_busy():
            self.channel.play(self.sound)

    def changeColor(self, color = (128, 128, 128)):
        if self.state_lock.acquire(False):
            self.image.fill(color)
            try:
                self.timer = threading.Timer(0.3, self.turnColorBack)
                self.timer.daemon = True
                self.timer.start()
            finally:
                self.state_lock.release()

    def turnColorBack(self):
        self.state_lock.acquire()
        self.image.fill(self.color)
        self.state_lock.release()

    def getColor(self):
        return self.color

class SampleListener(Leap.Listener):
    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        time.sleep(0.05)
        frame = controller.frame()
        iBox = frame.interaction_box
        # draw finger projection
        fingers = []
        for finger in frame.fingers:
            leapPoint = finger.stabilized_tip_position
            normalizedPoint = iBox.normalize_point(leapPoint, False)
            finger_pos = [normalizedPoint.x * 14 * WHITE_WIDTH, (1 - normalizedPoint.y) * 720]

            if finger_pos[0] < 14 * WHITE_WIDTH and finger_pos[0] > 0 and finger_pos[1] < 640 and finger_pos[1] > 0:
                if ((finger.tip_velocity.y < -300 or math.fabs(finger.tip_velocity.x) > 100 or math.fabs(finger.tip_velocity.x) + math.fabs(finger.tip_velocity.y) > 300)):
                    key_tap_event = pygame.event.Event(KEYTAP, fingerpos=finger_pos)
                    pygame.event.post(key_tap_event)

            fingers.append(finger_pos)

        if len(fingers) > 0:
            draw_finger_event = pygame.event.Event(KEYDRAWFINGERS, fingerspos=fingers)
            pygame.event.post(draw_finger_event)

def main():
    pygame.mixer.init()
    pygame.mixer.pre_init(44100, -16, 2, 1024 * 32)
    pygame.mixer.set_num_channels(24)
    pygame.font.init()
    title_font = pygame.font.SysFont('Comic Sans MS', 60)
    titleSurface = title_font.render('Cayano', False, (0, 0, 0))
    slogan_font = pygame.font.SysFont('Comic Sans MS', 40)
    sloganSurface = slogan_font.render('Enjoy music!', False, (0, 0, 0))
    pygame.init()

    white_key_num = 14
    size = white_key_num * WHITE_WIDTH, 720

    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Virtual Piano")

    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # enable the gesture
    controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
    controller.config.set("Gesture.KeyTap.MinDownVelocity", 40.0)
    controller.config.set("Gesture.KeyTap.HistorySeconds", .2)
    controller.config.set("Gesture.KeyTap.MinDistance", 3.0)
    controller.config.save()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    keys = []
    last_white_key = (0, 0)
    for i in range(len(FREQUENCY)):
        if (i == 1 or i == 3 or i == 6 or i == 8 or i == 10 or i == 13 or i == 15 or i == 18 or i == 20 or i == 22):
            left_top_pos = (keys[i - 1].left_top_pos[0] + WHITE_WIDTH - BLACK_WIDTH / 2, keys[i - 1].left_top_pos[1])
            key = Key(FREQUENCY[i], 300, "black", left_top_pos, osp.join(osp.join(osp.dirname("__file__"), "sounds"), "%i.wav" % i), pygame.mixer.Channel(i))
        else:
            if (i == 0):
                left_top_pos = (0, 0)
                last_white_key = left_top_pos
            else:
                left_top_pos = (last_white_key[0] + WHITE_WIDTH, last_white_key[1])
                last_white_key = left_top_pos
            key = Key(FREQUENCY[i], 300, "white", left_top_pos, osp.join(osp.join(osp.dirname("__file__"), "sounds"), "%i.wav" % i), pygame.mixer.Channel(i))
        keys.append(key)

    keyboard = Keyboard(keys)

    while 1:
        time.sleep(0.05)
        screen.fill((255, 255, 255))
        screen.blit(titleSurface, (600, 500))
        screen.blit(sloganSurface, (580, 600))

        for key in keyboard.keys:
            if (key.kind == "white"):
                screen.blit(key.image, key.left_top_pos)
                pygame.draw.rect(screen, (0, 0, 0), (key.left_top_pos[0], key.left_top_pos[1], WHITE_WIDTH, WHITE_HEIGHT), 3)

        for key in keyboard.keys:
            if (key.kind == "black"):
                screen.blit(key.image, key.left_top_pos)
                pygame.draw.rect(screen, (0, 0, 0), (key.left_top_pos[0], key.left_top_pos[1], BLACK_WIDTH, BLACK_HEIGHT), 3)

        has_drawn_fingers = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == KEYDRAWFINGERS and not has_drawn_fingers:
                for finger_pos in event.fingerspos:
                    if (len(finger_pos) > 0):
                        pygame.draw.circle(screen, (0, 0, 0), (int(finger_pos[0]), int(finger_pos[1])), 15, 3)
                has_drawn_fingers = True

            if event.type == KEYTAP:
                keyboard.press(keyboard.determineKeyPressed(event.fingerpos[0], event.fingerpos[1]))

        pygame.display.flip()

if __name__ == "__main__":
    main()