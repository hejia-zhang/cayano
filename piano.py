import Leap, sys
import pygame
import winsound
import time
import multiprocessing

BLACK_HEIGHT = 200
BLACK_WIDTH = 10
WHITE_HEIGHT = 500
WHITE_WIDTH = 50

# creating the event
KEYTAP = pygame.USEREVENT + 1
KEYDRAWFINGERS = pygame.USEREVENT + 2

FREQUENCY = [261, 277, 293, 311, 330, 349, 370, 392, 415, 440, 466, 494, 523, 554, 587, 622, 659, 699, 740, 784, 830, 880, 932, 988]

class Key:
    frequency = 0
    duration = 0
    color = (0, 0, 0)
    kind = "white"
    def __init__(self, frequency, duration, kind):
        self.frequency = frequency
        self.duration = duration
        self.kind = kind
        if (self.kind == "white"):
            color = (255, 255, 255)
        else:
            color = (0, 0, 0)

    def beep(self):
        winsound.Beep(self.frequency, self.duration)

    def changeColor(self):
        self.color = (0, 255, 0)

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
        posout.append((inx - self.minx) / (self.maxx - self.minx ) * 960)
        posout.append((inz - self.minz) / (self.maxz - self.minz ) * 640)

    def on_frame(self, controller):
        frame = controller.frame()
        # draw finger projection
        fingers = [];
        done = False;
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
    pygame.init()

    size = width, height = 960, 720
    key_num = 8
    key_range = range(0, width, width / key_num)
    speed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Virtual Piano")

    keyboard = pygame.image.load("keyboard.jpg")
    keyboard = pygame.transform.scale(keyboard, (width, height / 9 * 8))
    screen.blit(keyboard, (0, 0))

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
    for freq in FREQUENCY:
        if ()
        key = Key(freq, 300, "white")
        keys.append(key)

    # # Keep this process running until Enter is pressed
    # print "Press Enter to quit..."
    # try:
    #     sys.stdin.readline()
    # except KeyboardInterrupt:
    #     pass
    jobs = []
    while 1:
        # time.sleep(0.02)
        screen.blit(keyboard, (0, 0))
        # pygame.draw.circle(screen, (0, 125, 0), (450, 100), 20, 3)

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
                    p = multiprocessing.Process(target=keys[index].beep())
                    jobs.append(p)
                    p.start()

        pygame.display.flip()

if __name__ == "__main__":
    main()