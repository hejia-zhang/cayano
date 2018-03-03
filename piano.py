import Leap, sys
import pygame
import winsound

# creating the event
KEYTAP = pygame.USEREVENT + 1
KEYDRAWFINGERS = pygame.USEREVENT + 2

FREQUENCY = [261, 293, 330, 349, 392, 440, 494, 523]

class SampleListener(Leap.Listener):
    tap_num = 0

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        frame = controller.frame()

        # draw finger projection
        for finger in frame.fingers:
            #
            # print(finger.tip_position)
            draw_finger_event = pygame.event.Event(KEYDRAWFINGERS)
            pygame.event.post(draw_finger_event)

        for gesture in frame.gestures():
            if gesture.type is Leap.Gesture.TYPE_KEY_TAP:
                key_tap = Leap.KeyTapGesture(gesture)
                print("one key tap recorded! %i" % self.tap_num)
                self.tap_num = self.tap_num + 1
                key_tap_event = pygame.event.Event(KEYTAP)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == KEYTAP:
                print("Beep!")
                for freq in FREQUENCY:
                    winsound.Beep(freq, 300)
        pygame.display.flip()

if __name__ == "__main__":
    main()