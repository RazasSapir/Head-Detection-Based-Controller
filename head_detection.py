import cv2
import time
import pyautogui
import threading
import os

upper_cascade = cv2.CascadeClassifier(r"C:\Users\razsa\CyberTools\opencv-master\data\haarcascades\haarcascade_frontalface_default.xml")

CENTER_SIZE = 50
DOWN_HELP = -70
WIDTH = 540
HEIGHT = 380


class Player:
    def __init__(self, id, x, up, left, right, reset, drive, wait):
        self.id = id
        self.x = x
        self.Up = up
        self.Left = left
        self.Right = right
        self.Reset = reset
        self.drive = drive
        self.wait = wait
        self.center = None
        self.current = None
        self.calibrated = False
        self.currentButton = ""

    def drive_thread(self):
        while True:
            time.sleep(self.wait)
            pyautogui.keyDown(self.Up)
            print(str(self.id) + " - Drive:" + self.Up)
            time.sleep(self.drive)
            pyautogui.keyUp(self.Up)


def main():
    players = []
    video_capture = cv2.VideoCapture(0)
    # Set properties. Each returns === True on success (i.e. correct resolution)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    video_capture.set(cv2.CAP_PROP_FPS, 6)
    w = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    num_players = int(input("Insert num of Players: "))
    if num_players >= 1:
        players.append(Player(1, 0, 'Up', 'Left', 'Right', '\t', 0.5, 0.125))
    if num_players >= 2:
        players.append(Player(2, int(w / 2), 'w', 'a', 'd', '\b', 0.5, 0.125))

    for p in players:
        drive_thread = threading.Thread(target=p.drive_thread, args=())
        drive_thread.start()

    while True:
        #Capture frame-by-frame
        ret, frame = video_capture.read()
        frame = cv2.flip(frame, 1)
        k = cv2.waitKey(1)
        showCrop(frame, num_players)
        imgs = crop(frame, num_players)
        for p, img in zip(players, imgs):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            bodies = get_bodies(gray)
            if len(bodies) > 0:
                (x, y, w, h) = bodies[0]
                current = bodies[0]
                x += p.x
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if not p.calibrated:
                    if k % 256 == 13:
                        p.calibrated = True
                        p.center = current
                else:
                    (xC, yC, wC, hC) = p.center
                    cv2.rectangle(frame, (xC + p.x, yC), (xC + p.x + wC, yC + hC), (0, 0, 255), 2)
                    x_side = xC - current[0]
                    y_side = yC - current[1]
                    if x_side > CENTER_SIZE:
                        new_button = p.Left
                    elif x_side < -1*CENTER_SIZE:
                        new_button = p.Right
                    elif y_side < DOWN_HELP:
                        new_button = p.Reset
                        """drive_thread = threading.Thread(target=key_press, args=(p.Reset, 0.05))
                        drive_thread.start()
                        drive_thread.join(w)"""
                        print(str(p.id) + ": reset")
                    else:
                        new_button = p.Up
                    cv2.putText(frame, str(p.id) + " key: " + new_button, (p.x + 10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                                cv2.LINE_AA)
                    if new_button != p.Up:
                        # pyautogui.keyDown(new_button)
                        key_press(new_button, 0.2)
                        print(str(p.id) + ": " + new_button)
                    p.currentButton = new_button
        cv2.imshow('BodyDetection', frame)
        # ESC Pressed
        if k % 256 == 27:
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


def crop(img, splitby):
    img2 = img
    height, width, channels = img.shape
    # Number of pieces Horizontally
    CROP_W_SIZE = splitby
    # Number of pieces Vertically to each Horizontal
    CROP_H_SIZE = 1
    imgs = []
    for ih in range(CROP_H_SIZE):
        for iw in range(CROP_W_SIZE):
            x = int(width / CROP_W_SIZE * iw)
            y = int(height / CROP_H_SIZE * ih)
            h = int(height / CROP_H_SIZE)
            w = int(width / CROP_W_SIZE)
            img = img[y:y + h, x:x + w]
            imgs.append(img)
            img = img2
    return imgs


def showCrop(img, splitby):
    height, width, channels = img.shape
    # Number of pieces Horizontally
    CROP_W_SIZE = splitby
    # Number of pieces Vertically to each Horizontal
    CROP_H_SIZE = 1
    for ih in range(CROP_H_SIZE):
        for iw in range(CROP_W_SIZE):
            x = int(width / CROP_W_SIZE * iw)
            h = int(height / CROP_H_SIZE)
            cv2.line(img, (x, 0), (x, h), (0, 0, 0), 10)
    return img


def get_bodies(gray):
    bodies = upper_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=6,
        minSize=(50, 50),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return bodies


def key_press(key, wait):
    print(key)
    pyautogui.keyDown(key)
    time.sleep(wait)
    pyautogui.keyUp(key)


if __name__ == "__main__":
    main()



