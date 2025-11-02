import numpy as np
def calculate_bar_properties(node1_coord, node2_coord):
    """Tính chiều dài và góc của một thanh."""
    delta_x = node2_coord[0] - node1_coord[0]
    delta_y = node2_coord[1] - node1_coord[1]
    length = np.sqrt(delta_x**2 + delta_y**2)
    if length == 0:
        return 0, 0, 0 # Tránh lỗi chia cho 0
    
    c = delta_x / length # cos(angle)
    s = delta_y / length # sin(angle)
    return length, c, s
