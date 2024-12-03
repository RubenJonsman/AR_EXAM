import cv2
import numpy as np
import random
from tdmclient import ClientAsync

positions = []

class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.2, num_episodes=1000):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.num_episodes = num_episodes

        # Define state and action space
        self.states = ["left", "right", "forward", "idle"]
        self.actions = ["left", "right", "forward", "idle"]

        # Initialize Q-table with zeros
        self.q_table = np.zeros((len(self.states), len(self.actions)))

        # Mapping states and actions to indices for easier lookup
        self.state_to_index = {state: i for i, state in enumerate(self.states)}
        self.action_to_index = {action: i for i, action in enumerate(self.actions)}
        self.current_state = "idle"

    # Reward function (sample rewards; adjust based on your needs)
    def get_reward(self, state, action):
        if state == "forward" and action == "forward":
            return 10  # Reward for moving towards the ball
        elif state in ["left", "right"] and action == f"{state}":
            return 5   # Smaller reward for adjusting direction
        else:
            return -1  # Penalty for moving in the wrong direction

    def q_learning(self, ball_pos) -> str:

        ball_pos_index = self.state_to_index[ball_pos]
        # Epsilon-greedy action selection
        if random.uniform(0, 1) < self.epsilon:
            action = random.choice(self.actions)  # Explore: choose a random action
        else:
            action = self.actions[np.argmax(self.q_table[self.state_to_index[self.current_state]])]  # Exploit: choose best action from Q-table

        # Take action and observe reward
        reward = self.get_reward(self.current_state, action)
        next_state = ball_pos  # Simulate moving towards the ball

        # Q-learning update
        current_q_value = self.q_table[self.state_to_index[self.current_state], self.action_to_index[action]]
        max_future_q = np.max(self.q_table[self.state_to_index[next_state]])
        new_q_value = (1 - self.learning_rate) * current_q_value + self.learning_rate * (reward + self.discount_factor * max_future_q)
        self.q_table[self.state_to_index[self.current_state], self.action_to_index[action]] = new_q_value

        # Transition to the next state
        self.current_state = next_state
        return action

# The amount of pixels the ball needs to be off center, for the robot to move towards the opposite direction
class BallPositionDetector:
    def __init__(self, camera_index=0, fov=180, center_region_center=360, draw_contours=True, ball_sensitivity=100):
        self.camera = cv2.VideoCapture(camera_index)
        self.fov = fov
        self.center_region_center = center_region_center
        self.center_region_left_edge = center_region_center - fov // 2
        self.center_region_right_edge = center_region_center + fov // 2
        self.draw_contours = draw_contours
        self.positions = []

    def get_ball_relative_position(self):
        ret, frame = self.camera.read()

        if not ret:
            print("failed to grab frame")
            exit(1)

        # flip x
        flipped_frame = cv2.flip(frame, 1)
        # flip y
        flipped_frame = cv2.flip(flipped_frame, 0)
        blurred_frame = cv2.GaussianBlur(flipped_frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        # resize image

        # Blue
        lower_color = (36, 25, 50)
        upper_color = (70, 255, 255)

        # Red
        lower_color = (36, 25, 50)
        upper_color = (255, 70, 70)

        mask = cv2.inRange(hsv, lower_color, upper_color)
        blurred_frame = cv2.GaussianBlur(mask, (5, 5), 0)

        contours, _ = cv2.findContours(
            blurred_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cx = self.center_region_center
        ball_detected = False
        ball_count = 0
        for contour in contours:
            M = cv2.moments(contour)
            area = cv2.contourArea(contour)
            if area > 500:
                ball_count += 1
                ball_detected = True

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    self.positions.append([cx, cy])

        if self.draw_contours:
            contour_image = cv2.drawContours(blurred_frame, contours, -1, (0, 255, 0), 3)

            print("i see " + str(ball_count) + " balls")
            cv2.imwrite('./imgs/contour_image.jpg', contour_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.end()
            exit(0)

        if not ball_detected:
            return "left"

        if cx < self.center_region_left_edge:
            return "left"

        if cx > self.center_region_right_edge:
            return "right"

        return "forward"

    def end(self):
        self.camera.release()
        cv2.destroyAllWindows()

class ThymioController:
    def action_to_motor(self, action):
        action_to_speed = {
            "left": (1 * self.turning_speed_factor, -1 * self.turning_speed_factor),
            "forward": (1 * self.drive_speed_factor, 1 * self.drive_speed_factor),
            "right": (-1 * self.turning_speed_factor, 1 * self.turning_speed_factor),
            "idle": (0, 0)
        }

        return action_to_speed.get(action, (0, 0))

    def __init__(self, drive_speed_factor=250, turning_speed_factor=100):
        self.turning_speed_factor = turning_speed_factor
        self.drive_speed_factor = drive_speed_factor
        self.ball_position_detector = BallPositionDetector(draw_contours=True)
        self.q_learning = QLearningAgent()


        # Use the ClientAsync context manager to handle the connection to the Thymio robot.
        with ClientAsync() as client:

            async def prog():
                """
                Asynchronous function controlling the Thymio's behavior.
                """

                print("Connecting to Thymio")

                # Lock the node representing the Thymio to ensure exclusive access.
                with await client.lock() as node:

                    print("Starting Thymio")

                    # Wait for the robot's proximity sensors to be ready.
                    await node.wait_for_variables({"prox.horizontal"})

                    node.send_set_variables({"leds.top": [0, 0, 32]})
                    print("Thymio started successfully!")

                    try:
                        while True:
                            state = self.ball_position_detector.get_ball_relative_position()
                            action = self.q_learning.q_learning(state)

                            print("ACTION", action)
                            speeds = self.action_to_motor(action)
                            node.v.motor.left.target = speeds[1]
                            node.v.motor.right.target = speeds[0]
                            node.flush()  # Send the set commands to the robot.

                            await client.sleep(0.1)  # Pause for 0.3 seconds before the next iteration.

                    except KeyboardInterrupt:
                        node.v.motor.left.target = 0
                        node.v.motor.right.target = 0
                    # Once out of the loop, stop the robot and set the top LED to red.
                    print("Thymio stopped successfully!")
                    node.v.motor.left.target = 0
                    node.v.motor.right.target = 0
                    # node.v.leds.top = [32, 0, 0]
                    node.flush()

            # Run the asynchronous function to control the Thymio.
            client.run_async_program(prog)



def main():
    print("Starting Thymio controller")
    c = ThymioController()
    c.prog()

if __name__ == "__main__":
    main()
