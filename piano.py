import Leap, sys
import pygame
import winsound

# creating the event
KEYTAP = pygame.USEREVENT + 1
KEYDRAWFINGERS = pygame.USEREVENT + 2

FREQUENCY = [261, 293, 330, 349, 392, 440, 494, 523]

class SampleListener(Leap.Listener):
    tap_num = 0
    minx = -150
    maxx = 150
    minz = -25
    maxz = 75

    def on_connect(self, controller):
        print "Connected"

    def map2screen(self, inx, inz, posout):
        posout.append((inx - self.minx) / 300 * 960)
        posout.append((inz - self.minz) / 100 * 360)

    def on_frame(self, controller):
        frame = controller.frame()

        # draw finger projection
        fingers = []
        for finger in frame.fingers:
            # print(finger.tip_position)
            finger_pos = []
            if (finger.tip_position[0] > self.minx and finger.tip_position[0] < self.maxx
                    and finger.tip_position[2] > self.minz and finger.tip_position[2] < self.maxz):
                self.map2screen(finger.tip_position[0], finger.tip_position[2], finger_pos)
            fingers.append(finger_pos)

        if len(fingers) > 0:
            draw_finger_event = pygame.event.Event(KEYDRAWFINGERS, fingerspos = fingers)
            pygame.event.post(draw_finger_event)

        for gesture in frame.gestures():
            if gesture.type is Leap.Gesture.TYPE_KEY_TAP:
                key_tap = Leap.KeyTapGesture(gesture)
                print("one key tap recorded! %i" % self.tap_num)
                self.tap_num = self.tap_num + 1
                finger_pos = []
                self.map2screen(key_tap.position[0], key_tap.position[2], finger_pos)
                key_tap_event = pygame.event.Event(KEYTAP, fingerpos = finger_pos)
                pygame.event.post(key_tap_event)

                # print(key_tap.position)

        # print(frame.pointables.frontmost.tip_position)

def main():
    pygame.init()

    size = width, height = 960, 720
    key_num = 8
    speed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Virtual Piano")

    keyboard = pygame.image.load("keyboard.jpg")
    keyboard = pygame.transform.scale(keyboard, (width, height / 2))
    screen.blit(keyboard, (0, 0))

    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # enable the gesture
    controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
    controller.config.set("Gesture.KeyTap.MinDownVelocity", 40.0)
    controller.config.set("Gesture.KeyTap.HistorySeconds", .2)
    controller.config.set("Gesture.KeyTap.MinDistance", 1.0)
    controller.config.save()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # # Keep this process running until Enter is pressed
    # print "Press Enter to quit..."
    # try:
    #     sys.stdin.readline()
    # except KeyboardInterrupt:
    #     pass
    while 1:
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
                        print("one finger: ", finger_pos)
                has_drawn_fingers = True
                pygame.event.clear(KEYDRAWFINGERS)

            if event.type == KEYTAP:
                print("Beep!")
                for freq in FREQUENCY:
                    winsound.Beep(freq, 300)
        pygame.display.flip()

if __name__ == "__main__":
    main()