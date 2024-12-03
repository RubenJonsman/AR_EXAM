class ProximitySensor:
    def __init__(self, node):
        self.node = node

    def object_detection_approx_sensor(self):
        """
        Return back an array with 4 positions. 0 means no object within 10 cm, 1 means yes.
        """
        object_detection_array = [0, 0, 0, 0]
        front_left2 = self.node.v.prox.horizontal[0]    # Leftmost
        front_left1 = self.node.v.prox.horizontal[1]    # Left
        front_center = self.node.v.prox.horizontal[2]   # Center
        front_right1 = self.node.v.prox.horizontal[3]   # Right
        front_right2 = self.node.v.prox.horizontal[4]   # Rightmost
        back_left = self.node.v.prox.horizontal[5]      # Back left
        back_right = self.node.v.prox.horizontal[6]     # Back right
        if front_left2 > 0 or front_left1 > 0:
            object_detection_array[0] = 1
        if front_center > 0:
            object_detection_array[1] = 1
        if front_right1 > 0 or front_right2 > 0:
            object_detection_array[2] = 1
        if back_left > 0 or back_right > 0:
            object_detection_array[3] = 1

        return object_detection_array