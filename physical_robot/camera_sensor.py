from constants import AVOIDER, SEEKER, STATE_COLOR_MAP
import numpy as np
import cv2

lower_color = np.array([0, 106, 233])
upper_color = np.array([180, 255, 255])


class CameraSensor:
    def __init__(self, capture, type):
        self.capture = capture
        self.type = type

    def detect(self):
        ret, frame = self.capture.read()

        if not ret:
            print("failed to grab frame")
            exit(1)

        scale_factor = 0.25
        # scale_factor = 1

        frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)

        # flip x
        flipped_frame = cv2.flip(frame, 1)
        # flip y
        flipped_frame = cv2.flip(flipped_frame, 0)
        cv2.imwrite("./frame.jpg", flipped_frame)

        frame_width = flipped_frame.shape[0]

        # Apply blur to reduce noise
        blurred_frame = cv2.GaussianBlur(flipped_frame, (5, 5), 10)
        # cv2.imwrite("./imgs/blurred_frame.jpg", blurred_frame)

        # Convert to HSV
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

        lower_color = np.array([0, 106, 233])
        upper_color = np.array([180, 255, 255])

        mask = cv2.inRange(hsv, lower_color, upper_color)
        cv2.imwrite("./mask.jpg", mask)
        blurred_mask = cv2.GaussianBlur(mask, (3, 3), 0)

        contours, _ = cv2.findContours(
            blurred_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cx = frame_width // 2
        ball_detected = False
        ball_count = 0
        for contour in contours:
            M = cv2.moments(contour)
            area = cv2.contourArea(contour)
            if area > 30:
                print("Area: " + str(area))
                ball_count += 1
                ball_detected = True

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    # self.positions.append([cx, cy])

            else:
                print("Ignoring small area: " + str(area))

        print("i see " + str(ball_count) + " balls")
        # contour_image = cv2.drawContours(blurred_mask, contours, -1, (0, 255, 0), 3)
        # cv2.imwrite("./contour_image.jpg", contour_image)

        if ball_count > 0:
            # Calculate heading using the center of the ball
            return (cx / frame_width) * 2 - 1
        # if self.draw_contours:

        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit(0)

        if self.type == AVOIDER:
            # TODO: Detect red
            pass
        elif self.type == SEEKER:
            # TODO: Detect blue
            pass

    def get_color(self, robot):
        return STATE_COLOR_MAP[robot.type, robot.state]
