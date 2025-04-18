import sys
import os
from pathlib import Path

import pygame as pg
import pygame.freetype as freetype

project_dir = Path(__file__).parent.resolve()

pg.init()

# required symbols quantity
SYMBOLS_QUANTITY = 2000

# frames per second, the general speed of the program
FPS = 50
# reverse start timer
TIME_DELAY = 5

# window
is_wayland = ("WAYLAND_DISPLAY" in os.environ or
              "HYPRLAND_INSTANCE_SIGNATURE" in os.environ)

if is_wayland:
    DISPLAY_WIDTH = 1920
    DISPLAY_HEIGHT = 1080
    WINDOW_WIDTH = DISPLAY_WIDTH * .9
    WINDOW_HEIGHT = int(DISPLAY_HEIGHT * 0.2)
    os.environ['SDL_VIDEO_DRIVER'] = 'wayland'
    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.NOFRAME)
    scope_base = int(round(WINDOW_WIDTH ** .605 - 27))
else:
    DISPLAY_WIDTH = pg.display.Info().current_w
    DISPLAY_HEIGHT = pg.display.Info().current_h
    WINDOW_WIDTH = DISPLAY_WIDTH * 1
    WINDOW_HEIGHT = DISPLAY_HEIGHT * .2
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
        int(round(DISPLAY_WIDTH * .328)), int(round(DISPLAY_WIDTH * .7)))
    scope_base = int(round(WINDOW_WIDTH ** .605 - 27))
    pg.display.set_caption("Typing speed test")
    screen = pg.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])

# colors
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
TEXT_LIST_COLOR = (100, 100, 100)
HEAD_TEXT_COLOR = (255, 255, 255)

# fonts
FONT_NAME_LIST = ["Calibri"]
FONT_NAME_HEAD = ["Calibri"]
FONT_SIZE_HEAD = int(round(scope_base * .9))
FONT_SIZE_LIST = scope_base

# text positioning
# x center position of typing zone from center to left
DRIFT_TYPPING = int(round(scope_base * 2.3))
# x center position of SYMBOLS_QUANTITY from left border to center
DRIFT_COUNTER = int(round(scope_base * 2.7))
RECT_HIGH = int(round(scope_base * 1.2))
TEXT_HIGH = int(round(scope_base * 1.5))

# sound
pg.mixer.init()
sound1 = pg.mixer.Sound(project_dir / "start-count-3-sec.mp3")
sound1.set_volume(0.1)
sound2 = pg.mixer.Sound(project_dir / 'stop.mp3')
sound2.set_volume(0.5)


def color_bg_mix(counter):
    """
        start (150, 150, 255)
        midle (100, 255, 100)
        end   (255,  0,   0 )

        :param counter: tapped symbols counter
        :return: head bg color
        """
    half_1 = round(SYMBOLS_QUANTITY / 2)
    half_2 = SYMBOLS_QUANTITY - half_1
    grad_1_1 = 50 / half_1
    grad_1_2 = 155 / half_2
    grad_2_1 = 105 / half_1
    grad_2_2 = 255 / half_2
    grad_3_1 = 155 / half_1
    grad_3_2 = 100 / half_2
    if counter <= half_1:
        t_1 = 150 - (grad_1_1 * counter)
        t_2 = 150 + (grad_2_1 * counter)
        t_3 = 255 - (grad_3_1 * counter)
    else:
        counter_2 = counter - half_1
        t_1 = 100 + (grad_1_2 * counter_2)
        t_2 = 255 - (grad_2_2 * counter_2)
        t_3 = 100 - (grad_3_2 * counter_2)
    return t_1, t_2, t_3


def color_text_mix(counter):
    """
    start (255, 255, 255)
    midle (255,  0,   0 )
    end   ( 0,   0,   0 )

    :param counter: tapped symbols counter
    :return: head text color
    """
    half_1 = round(SYMBOLS_QUANTITY / 3)
    half_2 = SYMBOLS_QUANTITY - half_1
    grad_1_2 = 255 / half_2
    grad_2_1 = 255 / half_1
    grad_3_1 = 255 / half_1
    if counter <= half_1:
        t_1 = 255
        t_2 = 255 - (grad_2_1 * counter)
        t_3 = 255 - (grad_3_1 * counter)
    else:
        counter_2 = counter - half_1
        t_1 = 255 - (grad_1_2 * counter_2)
        t_2 = 0
        t_3 = 0
    return t_1, t_2, t_3


# Another color version (use only 1):

# def color_text_mix(counter):
#     """
#         start (255, 255, 255)
#         midle ( 0,   0,  255)
#         end   ( 0,   0,   0 )
#
#         :param counter: tapped symbols counter
#         :return: head text color
#         """
#     half_1 = round(SYMBOLS_QUANTITY / 3)
#     half_2 = SYMBOLS_QUANTITY - half_1
#     grad_1_1 = 255 / half_1
#     grad_2_1 = 255 / half_1
#     grad_3_2 = 255 / half_2
#     if counter <= half_1:
#         t_1 = 255 - (grad_1_1 * counter)
#         t_2 = 255 - (grad_2_1 * counter)
#         t_3 = 255
#     else:
#         counter_2 = counter - half_1
#         t_1 = 0
#         t_2 = 0
#         t_3 = 255 - (grad_3_2 * counter_2)
#     return t_1, t_2, t_3


# Another color version (use only 1):

# def color_text_mix(counter):
#     """
#         start (255, 255, 255)
#         end   ( 0,   0,   0 )
#
#         :param counter: tapped symbols counter
#         :return: head text color
#         """
#     step_grad = 255 / SYMBOLS_QUANTITY
#     tone = 255 - (counter * step_grad)
#     return tone, tone, tone

def color_bg_wait_mix(timer, delay):
    """
        start (155, 155, 155)
        end   (155, 155, 255)

        :param timer: msec time wait period from 0 to (delay * 1000);
        :param delay: length of "wait" function
        :return: head bg color
        """
    delay_inner = delay * 1000
    step_grad = 100 / delay_inner
    t_3 = 155 + (timer * step_grad)
    return 155, 155, t_3


class Secundomer:
    """Secundomer

    y - height coodinate in pixels,
    delay - delay in seconds before the test starts"""

    def __init__(self, y, delay, start, color):
        self.y = y
        self.delay = delay
        self.start = start
        self.color = color
        self.font = pg.font.SysFont(FONT_NAME_HEAD, FONT_SIZE_HEAD)

    def run(self):
        timer_sec = round(
            (pg.time.get_ticks() - self.start) / 1000) - self.delay
        minutes = int(timer_sec / 60)
        seconds = timer_sec - (minutes * 60)
        secundomer = f"{minutes} : {seconds}"
        text = self.font.render(secundomer, True, self.color)
        text_rect = text.get_rect()
        text_rect.centerx = screen.get_rect().centerx
        text_rect.y = self.y
        screen.blit(text, text_rect)


class Counter:
    """
    Visual counter of typed symbols

    x, y - position
    """

    def __init__(self, counter, x, y, color):
        self.font = pg.font.SysFont(FONT_NAME_HEAD, FONT_SIZE_HEAD)
        self.x = x
        self.y = y
        self.counter = counter
        self.color = color

    def run(self):
        count = f"{SYMBOLS_QUANTITY - self.counter}"
        text = self.font.render(count, True, self.color)
        text_rect = text.get_rect()
        text_rect.x = self.x
        text_rect.y = self.y
        screen.blit(text, text_rect)


class TextInput:
    """
    A simple TextInput class that allows you to receive inputs in pygame.
    Based on pygame package's example file.
    """

    def __init__(
            self, prompt: str, pos, screen_dimensions,
            print_event: bool, text_color=TEXT_COLOR,
            text_list_color=TEXT_LIST_COLOR
    ) -> None:
        self.FONT_NAME_LIST = FONT_NAME_LIST
        self.prompt = prompt  # sign '>'
        self.print_event = print_event  # bool
        # position of chatlist and chatbox
        self.CHAT_LIST_POS = pg.Rect(
            (pos[0] - 20, pos[1]), (WINDOW_WIDTH / 2 - DRIFT_TYPPING, 40))
        self.CHAT_BOX_POS = pg.Rect(
            (pos[0], pos[1] + 3), (screen_dimensions[1], 40))

        # pos = (x, y) - input coodinates
        self.pos_0 = pos[0]
        self.chat_box_editing = False
        self.chat_box_text = ""  # current moment typing word, chat_box
        self.chat_box_text_pos = 0  # cursor position in chat_box
        self.chat_box_editing_text = ""
        self.chat_box_editing_pos = 0
        self.chat_list = []  # list of already typed words (class list)
        self.list_string = ''  # string of already typed words (class str)

        self.width_list_string = 0

        self.counter = 0  # counter of typed symbols

        self.font = freetype.SysFont(self.FONT_NAME_LIST, FONT_SIZE_LIST)
        self.text_color = text_color
        self.text_list_color = text_list_color

    def update(self, events) -> None:
        """
        Updates the text input widget
        """
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key not in {pg.K_SPACE, pg.K_RIGHT, pg.K_LEFT,
                                     pg.K_UP, pg.K_DOWN, pg.K_BACKSPACE,
                                     pg.K_DELETE, pg.K_ESCAPE, pg.K_PRINT,
                                     pg.K_SCROLLLOCK, pg.K_PAUSE, pg.K_NUMLOCK,
                                     pg.K_RETURN, pg.K_CAPSLOCK, pg.K_END,
                                     pg.K_HOME, pg.K_LALT, pg.K_TAB,
                                     pg.K_LSHIFT, pg.K_LCTRL, pg.K_RALT,
                                     pg.K_RSHIFT, pg.K_RCTRL, pg.K_INSERT,
                                     pg.K_END, pg.K_PAGEUP, pg.K_PAGEDOWN,
                                     pg.K_F1, pg.K_F2, pg.K_F3, pg.K_F4,
                                     pg.K_F5, pg.K_F6, pg.K_F7, pg.K_F8,
                                     pg.K_F9, pg.K_F10, pg.K_F11, pg.K_F12,
                                     1073742051, 1073741925, 1073742085,
                                     1073742086, 1073741953, 1073741952,
                                     1073742093, 1073742089, 1073742108,
                                     1073741907, 1073741912,
                                     }:
                    self.counter += 1

                if self.chat_box_editing:
                    if len(self.chat_box_editing_text) == 0:
                        self.chat_box_editing = False
                    continue

                if event.key == pg.K_BACKSPACE:
                    if len(self.chat_box_text) > 0 and self.chat_box_text_pos > 0:
                        self.chat_box_text = (
                            self.chat_box_text[0: self.chat_box_text_pos - 1]
                            + self.chat_box_text[self.chat_box_text_pos:]
                        )
                        self.chat_box_text_pos = max(
                            0, self.chat_box_text_pos - 1)
                        self.counter -= 1

                elif event.key == pg.K_DELETE:
                    if self.chat_box_text_pos < len(self.chat_box_text):
                        self.counter -= 1
                    self.chat_box_text = (
                        self.chat_box_text[0: self.chat_box_text_pos]
                        + self.chat_box_text[self.chat_box_text_pos + 1:]
                    )

                elif event.key == pg.K_LEFT:
                    self.chat_box_text_pos = max(0, self.chat_box_text_pos - 1)
                    # self.counter -= 1
                elif event.key == pg.K_RIGHT:
                    self.chat_box_text_pos = min(
                        len(self.chat_box_text), self.chat_box_text_pos + 1
                    )

                # Handle ENTER key
                elif event.key in [pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE]:
                    # Block if we have no text to append
                    if len(self.chat_box_text) == 0:
                        continue

                    # Append chat list
                    self.list_string += self.chat_box_text
                    self.chat_list.append(self.chat_box_text)
                    self.chat_box_text = ""
                    self.chat_box_text_pos = 0

            elif event.type == pg.TEXTEDITING:
                if self.print_event:
                    print(event)
                self.chat_box_editing = True
                self.chat_box_editing_text = event.text
                self.chat_box_editing_pos = event.start

            elif event.type == pg.TEXTINPUT:
                if self.print_event:
                    print(event)
                self.chat_box_editing = False
                self.chat_box_editing_text = ""
                self.chat_box_text = (
                    self.chat_box_text[0: self.chat_box_text_pos]
                    + event.text
                    + self.chat_box_text[self.chat_box_text_pos:]
                )
                self.chat_box_text_pos += len(event.text)

    def draw(self, screen_2: pg.Surface) -> None:
        """
        Draws the text input widget onto the provided surface
        """

        rect_list_string = self.font.render_to(
            surf=screen_2,
            dest=(self.CHAT_LIST_POS.x -
                  (15 + self.width_list_string), self.CHAT_LIST_POS.y),
            text=self.list_string,
            fgcolor=self.text_list_color,
        )
        self.width_list_string = rect_list_string.width

        if self.width_list_string > round(WINDOW_WIDTH / 2):
            self.list_string = self.list_string[5:]

        start_pos = self.CHAT_BOX_POS.copy()
        ime_text_l = self.prompt + \
            self.chat_box_text[0: self.chat_box_text_pos]
        ime_text_m = (
            self.chat_box_editing_text[0: self.chat_box_editing_pos]
            + "|"
            + self.chat_box_editing_text[self.chat_box_editing_pos:]
        )
        ime_text_r = self.chat_box_text[self.chat_box_text_pos:]

        rect_text_l = self.font.render_to(
            screen_2, start_pos, ime_text_l, self.text_color
        )
        start_pos.x += rect_text_l.width

        self.font.render_to(
            screen_2,
            start_pos,
            ime_text_m,
            self.text_color,
        )

        self.font.render_to(
            surf=screen_2,
            dest=start_pos,
            text=ime_text_r,
            fgcolor=self.text_color,
        )


def head_rect_color(color):
    """
    Colors head rectangle with passed color (background)
    """
    pg.draw.rect(
        color=color,
        surface=screen,
        rect=(0, 0, WINDOW_WIDTH, RECT_HIGH)
    )


def wait(timer, delay=TIME_DELAY):
    """ Time count-down before tapping biggins function

            :param timer: msec time wait period from 0 to (delay * 1000);
            :param delay: length of "wait" function
            :return: None
            """
    head_rect_color(color_bg_wait_mix(timer, delay))
    warning = "get ready..."
    if timer > 1362:
        sound1.play()
    d = 800
    if timer > 1400:
        warning = "1.."
    if timer > 1400 + d:
        warning = "2.."
    if timer > 1410 + d * 2:
        warning = "3.."
    if timer > 1420 + d * 3:
        warning = "4.."

    text = pg.font.SysFont(FONT_NAME_HEAD, FONT_SIZE_HEAD).render(
        warning, True, HEAD_TEXT_COLOR)
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.y = int(round(scope_base * .13))
    screen.blit(text, text_rect)
    pg.display.update()


def greet():
    head_rect_color((150, 150, 150))
    greeting = "Press Enter/SPACE"
    text = pg.font.SysFont(FONT_NAME_HEAD, FONT_SIZE_HEAD).render(
        greeting, True, HEAD_TEXT_COLOR)
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.y = int(round(scope_base * .13))
    screen.blit(text, text_rect)
    pg.display.update()


class Game:
    """
    A class that handles the game's events, mainloop etc.
    """

    def __init__(self) -> None:

        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.FPS = FPS
        self.BG_COLOR = BG_COLOR
        self.screen = pg.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pg.time.Clock()

        # Text input
        # Set to true or add 'showevent' in argv to see IME and KEYDOWN events
        self.print_event = "showevent" in sys.argv
        self.text_input = TextInput(
            prompt="> ",
            # input coodinates
            pos=(screen.get_rect().centerx - DRIFT_TYPPING, TEXT_HIGH),
            screen_dimensions=(self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            print_event=self.print_event,
            text_color=TEXT_COLOR,
        )
        self.counter = SYMBOLS_QUANTITY
        self.greeting = True
        self.get_ready = False
        self.tapping_start = False
        self.tapping_stop = False

    def main_loop(self) -> None:
        pg.key.start_text_input()
        input_rect = pg.Rect(80, 80, 320, 40)
        pg.key.set_text_input_rect(input_rect)
        screen.fill(BG_COLOR)
        pg.display.update()
        time_start = 0
        running = True

        while running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    return
            # Greeting
            if self.greeting:
                greet()
                for event in events:
                    if event.type == pg.KEYDOWN:
                        if event.key == 13 or event.key == pg.K_SPACE:
                            time_start = pg.time.get_ticks()
                            # sound1.play()
                            self.greeting = False
                            self.get_ready = True

            # countdown
            elif self.get_ready:
                head_rect_color((150, 150, 150))
                wait(pg.time.get_ticks() - time_start)
                time_from_enter = round(
                    (pg.time.get_ticks() - time_start) / 1000)
                if time_from_enter >= TIME_DELAY:
                    self.get_ready = False
                    self.tapping_start = True

            # text typing
            elif self.tapping_start:
                self.text_input.update(events)
                # Screen updates
                self.screen.fill(self.BG_COLOR)
                head_rect_color(color_bg_mix(self.text_input.counter))

                secundomer = Secundomer(
                    y=int(round(scope_base * .13)),
                    delay=TIME_DELAY,
                    start=time_start,
                    color=color_text_mix(self.text_input.counter)
                )
                secundomer.run()

                self.text_input.draw(self.screen)
                self.counter = Counter(
                    counter=self.text_input.counter,
                    x=WINDOW_WIDTH - DRIFT_COUNTER,
                    y=int(round(scope_base * .13)),
                    color=color_text_mix(self.text_input.counter)
                )
                self.counter.run()

                pg.display.update()
                self.clock.tick(self.FPS)

                if self.text_input.counter >= SYMBOLS_QUANTITY:
                    self.tapping_start = False
                    self.tapping_stop = True
                    sound2.play()


if __name__ == '__main__':
    game = Game()
    game.main_loop()
