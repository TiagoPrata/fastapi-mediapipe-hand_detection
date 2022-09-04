import base64
import io
import math
import numpy as np
from PIL import Image
import mediapipe as mp
import cv2


def base64str_to_PILImage(base64str):
    """Convert a Base64 Image to a Pillow Image

    Args:
        base64str (str): Image in Base64 string

    Returns:
        Image: Pillow image (https://pillow.readthedocs.io/en/stable/reference/Image.html)
    """

    base64_img_bytes = base64str.encode('utf-8')
    base64bytes = base64.b64decode(base64_img_bytes)
    bytesObj = io.BytesIO(base64bytes)
    img = Image.open(bytesObj)
    return img


def PILImage_to_base64str(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return img_str.decode()


def base64img_to_np_array(image: str):
    pillow_img = base64str_to_PILImage(image)
    return np.array(pillow_img)


def np_array_to_base64img(image):
    pillow_img = Image.fromarray(image)
    return PILImage_to_base64str(pillow_img)


class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.static_image_mode, self.max_num_hands, self.model_complexity,
                                        self.min_detection_confidence, self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils
        
        self.angle = None

    def putText(self, text: str, location, fontScale = 3, color = (255,0,0), thickness = 3):
        cv2.putText(self.img, text, location, cv2.FONT_HERSHEY_COMPLEX, fontScale, color, thickness)

    def _unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def _angle_between(self, v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = self._unit_vector(v1)
        v2_u = self._unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


    def processed_img(self):
        return np_array_to_base64img(self.img)


    def process_hands(self, img_base64: str):
        self.img = base64img_to_np_array(img_base64)
        self.results = self.hands.process(self.img)


    def find_hands(self):
        if self.results.multi_hand_landmarks:
            for hand_landmark in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(self.img, hand_landmark, self.mpHands.HAND_CONNECTIONS)


    def find_position(self, hand_num = 0):
        landmark_list = []

        if self.results.multi_hand_landmarks:
            selected_hand = self.results.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(selected_hand.landmark):
                h,w,c = self.img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([id, cx, cy])

        return landmark_list


    def get_thumb_index_points(self):
        x1, y1, x2, y2 = None, None, None, None
        landmark_list = self.find_position()
        has_items = len(landmark_list) > 0
        if has_items:
            x1, y1 = landmark_list[4][1], landmark_list[4][2]
            x2, y2 = landmark_list[8][1], landmark_list[8][2]

        return has_items, x1, y1, x2, y2

    
    def find_thumb_and_index(self):
        has_items, x1, y1, x2, y2 = self.get_thumb_index_points()
        if has_items:
            cv2.circle(self.img, (x1,y1), 15, (255,0,255), cv2.FILLED)
            cv2.circle(self.img, (x2,y2), 15, (255,0,255), cv2.FILLED)


    def line_between_thumb_and_index(self):
        has_items, x1, y1, x2, y2 = self.get_thumb_index_points()
        if has_items:
            cv2.arrowedLine(self.img, (x1,y1), (x2,y2), (255,0,255), 3)

    def draw_circle_in_the_arrow(self, color = (255, 0, 255)):
        has_items, x1, y1, x2, y2 = self.get_thumb_index_points()
        if has_items:
            cx, cy = (x1 + x2) // 2, (y1 +y2) // 2
            cv2.circle(self.img, (cx, cy), 15, color, cv2.FILLED)

    def get_arrow_length(self):
        length = None
        has_items, x1, y1, x2, y2 = self.get_thumb_index_points()
        if has_items:
            length = math.hypot(x2 - x1, y2 - y1)

        return length

    def calc_arrow_angle(self):
        has_items, x1, y1, x2, y2 = self.get_thumb_index_points()
        if has_items:
            v1 = self._unit_vector((x2-x1,y2-y1))
            v2 = self._unit_vector((1,0))
            self.angle = self._angle_between(v1, v2)
            self.angle = self.angle / math.pi

