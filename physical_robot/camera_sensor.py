from constants import AVOIDER, SEEKER, STATE_COLOR_MAP
import numpy as np
import cv2

lower_color = np.array([0, 106, 233])
upper_color = np.array([180, 255, 255])


class CameraSensor:
    def __init__(self, capture, type):
        self.capture = capture
        self.type = type
        self.simulation_scaler = 8

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
        # cv2.imwrite("./frame.jpg", flipped_frame)

        frame_width = flipped_frame.shape[0]

        # Apply blur to reduce noise
        blurred_frame = cv2.GaussianBlur(flipped_frame, (5, 5), 10)
        # cv2.imwrite("./imgs/blurred_frame.jpg", blurred_frame)

        # Convert to HSV
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

        lower_red = np.array([158, 36, 210])
        upper_red = np.array([180, 255, 255])

        lower_blue = np.array([69, 109, 207])
        upper_blue = np.array([180, 255, 255])
        # lower_blue = np.array([0, 106, 233])
        # upper_blue = np.array([180, 255, 255])

        lower_color = lower_blue if self.type == SEEKER else lower_red
        upper_color = upper_blue if self.type == SEEKER else upper_red

        mask = cv2.inRange(hsv, lower_color, upper_color)
        # cv2.imwrite("./mask.jpg", mask)
        blurred_mask = cv2.GaussianBlur(mask, (3, 3), 0)
        distance_to_wall = self.get_distance_and_angle_to_wall(blurred_mask)
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
                # print("Area: " + str(area))
                ball_count += 1
                ball_detected = True

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    # self.positions.append([cx, cy])

            else:
                print("Ignoring small area: " + str(area))

        print("i see " + str(ball_count) + " contours")
        # contour_image = cv2.drawContours(blurred_mask, contours, -1, (0, 255, 0), 3)
        # cv2.imwrite("./contour_image.jpg", contour_image)

        if ball_count > 0:
            distance_to_robot = self.get_distance_to_robot_in_view(blurred_mask)
            # print(distance_to_robot)

            center_region_size = 150 * scale_factor
            center_region_center = 320 * scale_factor
            center_region_left_edge = center_region_center - center_region_size
            center_region_right_edge = center_region_center + center_region_size
            if cx < center_region_left_edge:
                relative_robot_position = "left"
            elif cx > center_region_right_edge:
                relative_robot_position = "right"
            else:
                relative_robot_position = "center"

            # Calculate heading using the center of the ball
            return (
                (cx / frame_width) * 2 - 1,
                True,
                relative_robot_position,
                distance_to_robot,
                distance_to_wall,
            )
        else:
            return None, False, None, None, None
        # if self.draw_contours:

    def get_color(self, robot):
        return STATE_COLOR_MAP[robot.type, robot.state]

    def get_distance_and_angle_to_wall(self, mask):
        "Calculates the distance to the wall (black strip of tape on ground)"
        # Find the contours of the black strip (wall)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Calculate the distance to the nearest wall
        nearest_distance = float("inf")
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            distance = (
                y  # Assuming the y-coordinate represents the distance to the wall
            )
            if distance < nearest_distance:
                nearest_distance = distance

        return nearest_distance

    def get_distance_to_robot_in_view(self, mask):
        # Assuming a known width of the robot in real life (in meters)
        KNOWN_ROBOT_WIDTH = 0.5

        # Focal length of the camera (in pixels)
        FOCAL_LENGTH = 700

        # Find the bounding box of the largest contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the distance to the robot
        distance = ((KNOWN_ROBOT_WIDTH * FOCAL_LENGTH) / w) * self.simulation_scaler
        return distance
