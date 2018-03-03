import Leap, sys
import pygame
import winsound
import time
import multiprocessing

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
class Key:
    frequency = 0
    duration = 0
    color = (0, 0, 0)
    kind = "white"
    left_top_pos = [0, 0]
    image = pygame.Surface((WHITE_WIDTH, WHITE_HEIGHT))
    def __init__(self, frequency, duration, kind, left_top_pos, sound_path):
        self.frequency = frequency
        self.duration = duration
        self.kind = kind
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
        self.sound = pygame.mixer.Sound(sound_path)

    def beep(self):
        # winsound.Beep(self.frequency, self.duration)
        self.sound.play()

    def changeColor(self, color = (0, 255, 0)):
        self.color = color
        self.image.fill(color)

    def getColor(self):
        return self.color

class SampleListener(Leap.Listener):
    tap_num = 0
    fingerNums = ['thumb', 'index', 'middle', 'ring', 'pinky'];
    handNums = ['left', 'right'];
    minx = -100
    maxx = 100
    minz = -50
    maxz = 50

    def on_connect(self, controller):
        print "Connected"

    def map2screen(self, inx, inz, posout):
        posout.append((inx - self.minx) / (self.maxx - self.minx ) * 14 * WHITE_WIDTH)
        posout.append((inz - self.minz) / (self.maxz - self.minz ) * 640)

    def on_frame(self, controller):
        frame = controller.frame()
        # draw finger projection
        fingers = []
        done = False
        for i, hand in enumerate(frame.hands):
            for j, finger in enumerate(hand.fingers):
                finger_pos = []
                if (finger.tip_position.x > self.minx and finger.tip_position.x < self.maxx
                        and finger.tip_position.z > self.minz and finger.tip_position.z < self.maxz):
                    self.map2screen(finger.tip_position.x, finger.tip_position.z, finger_pos)

                    if (finger.tip_velocity.z < -750):
                        temp = [finger.tip_position.x, finger.tip_position.z];
                    else:
                        temp = [];

                    if (temp and done == False):  # true if finger is tapping
                        print("Tap recorded " + self.handNums[i] + " " + self.fingerNums[j])
                        self.tap_num = self.tap_num + 1
                        # tappingFingers.append(temp);
                        self.map2screen(temp[0], temp[1], finger_pos)
                        key_tap_event = pygame.event.Event(KEYTAP, fingerpos=finger_pos)
                        pygame.event.post(key_tap_event)
                        done = True;

                fingers.append(finger_pos);

        if len(fingers) > 0:
            draw_finger_event = pygame.event.Event(KEYDRAWFINGERS, fingerspos=fingers)
            pygame.event.post(draw_finger_event)

def main():
    pygame.mixer.init()
    pygame.mixer.pre_init(44100, -16, 24, 1024 * 24)
    pygame.init()

    key_num = len(FREQUENCY)
    white_key_num = 14
    size = width, height = white_key_num * WHITE_WIDTH, 720
    key_range = range(0, width, width / key_num)
    speed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Virtual Piano")

    # keyboard = pygame.image.load("keyboard.jpg")
    # keyboard = pygame.transform.scale(keyboard, (width, height / 9 * 8))
    # screen.blit(keyboard, (0, 0))

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
            key = Key(FREQUENCY[i], 300, "black", left_top_pos, "D:\HackTech2018\sounds\%i.wav" % i)
        else:
            if (i == 0):
                left_top_pos = (0, 0)
                last_white_key = left_top_pos
            else:
                left_top_pos = (last_white_key[0] + WHITE_WIDTH, last_white_key[1])
                last_white_key = left_top_pos
            key = Key(FREQUENCY[i], 300, "white", left_top_pos, "D:\HackTech2018\sounds\%i.wav" % i)
        keys.append(key)

    keyboard = Keyboard(keys)

    # # Keep this process running until Enter is pressed
    # print "Press Enter to quit..."
    # try:
    #     sys.stdin.readline()
    # except KeyboardInterrupt:
    #     pass
    jobs = []
    while 1:
        # time.sleep(0.02)
        screen.fill((255, 255, 255))

        # pygame.draw.circle(screen, (0, 125, 0), (450, 100), 20, 3)
        # draw every keys

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
                        # print("one finger: ", finger_pos)
                has_drawn_fingers = True
                # pygame.event.clear(KEYDRAWFINGERS)

            if event.type == KEYTAP:
                print("Beep!")
                index = -1
                for i in key_range:
                    if (i <= event.fingerpos[0]):
                        index += 1
                    else:
                        break
                print("Index: ", index)
                print(event.fingerpos)
                if (index > -1):
                    keyboard.keys[index].beep()
                    keyboard.keys[index].changeColor()

        pygame.display.flip()

if __name__ == "__main__":
    main()