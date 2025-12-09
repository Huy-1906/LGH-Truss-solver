import numpy as np
import streamlit as st
from .calculate_bar_properties import calculate_bar_properties

def solve_general_truss(nodes, bars, supports, external_forces):
    """
    Giải hệ giàn 2D tổng quát với gối tựa có góc xoay.
    supports: dict {node_name: {'type': 'pin'/'roller', 'angle': degree}}
    """
    
    node_names = list(nodes.keys())
    num_nodes = len(node_names)
    num_bars = len(bars)
    
    # 1. Xác định số ẩn (Nội lực thanh + Phản lực gối)
    # Phản lực được lưu dạng: (Node, Type, Angle, Index_in_matrix)
    reaction_unknowns = [] 
    
    for name in node_names:
        if name in supports:
            sup = supports[name]
            s_type = sup['type']
            s_angle = sup['angle'] # Độ
            
            if s_type == 'pin':
                # Gối cố định: Luôn có 2 phản lực vuông góc (Rx, Ry cục bộ hoặc toàn cục)
                # Để đơn giản, ta giải theo hệ tọa độ toàn cục X, Y cho gối cố định
                reaction_unknowns.append({'node': name, 'dir': 'x', 'angle': 0})
                reaction_unknowns.append({'node': name, 'dir': 'y', 'angle': 90})
            elif s_type == 'roller':
                # Gối di động: Chỉ có 1 phản lực vuông góc với mặt trượt
                # Mặt trượt nghiêng alpha -> Phản lực nghiêng alpha + 90
                reaction_unknowns.append({'node': name, 'dir': 'normal', 'angle': s_angle + 90})

    num_reactions = len(reaction_unknowns)
    num_unknowns = num_bars + num_reactions
    num_eq = 2 * num_nodes
    
    # 2. Xây dựng ma trận
    A = np.zeros((num_eq, num_unknowns)) 
    F_ext = np.zeros(num_eq)
    
    for i, node_name in enumerate(node_names):
        eq_x = 2 * i
        eq_y = 2 * i + 1
        
        # 2a. Ngoại lực
        force = external_forces.get(node_name, [0, 0])
        F_ext[eq_x] = force[0]
        F_ext[eq_y] = force[1]
        
        # 2b. Nội lực thanh (Bar Forces)
        for j, bar_nodes in enumerate(bars):
            n1, n2 = tuple(sorted(bar_nodes))
            
            if n1 == node_name:
                curr, other = nodes[n1], nodes[n2]
                sign = 1 # Vector hướng ra khỏi nút đang xét
            elif n2 == node_name:
                curr, other = nodes[n2], nodes[n1]
                sign = 1 
            else:
                continue
            
            # Tính cos, sin của thanh hướng từ nút đang xét -> nút kia
            # Tuy nhiên hàm calculate trả về vector dương.
            # Với phương pháp nút: Tổng F = 0.
            # Giả sử lực thanh là Kéo (Tension, dương) -> Lực tác dụng lên nút hướng ra xa nút.
            # Vector đơn vị u = (other - curr) / L
            
            dx = other[0] - curr[0]
            dy = other[1] - curr[1]
            L = np.sqrt(dx**2 + dy**2)
            if L == 0: c, s = 0, 0
            else: c, s = dx/L, dy/L
            
            # Hệ số trong ma trận
            A[eq_x, j] = c
            A[eq_y, j] = s

        # 2c. Phản lực (Reaction Forces)
        for k, reac in enumerate(reaction_unknowns):
            if reac['node'] == node_name:
                # Góc của phản lực (đã tính toán là vuông góc mặt trượt với roller)
                angle_rad = np.radians(reac['angle'])
                r_cos = np.cos(angle_rad)
                r_sin = np.sin(angle_rad)
                
                col_index = num_bars + k
                A[eq_x, col_index] = r_cos
                A[eq_y, col_index] = r_sin

    # 3. Giải hệ
    try:
        if num_eq != num_unknowns:
            st.error(f"Hệ siêu tĩnh hoặc biến hình! Số PT ({num_eq}) != Số ẩn ({num_unknowns}).")
            return None, None
            
        X = np.linalg.solve(A, -F_ext)
        
        bar_vals = X[:num_bars]
        reac_vals = X[num_bars:]
        
        # Format kết quả
        bar_results = {f"S_{sorted(bars[i])[0]}-{sorted(bars[i])[1]}": f for i, f in enumerate(bar_vals)}
        
        reaction_results = {}
        for i, r_val in enumerate(reac_vals):
            r_info = reaction_unknowns[i]
            # Lưu cả thông tin góc để vẽ vector phản lực cho đúng
            key = f"R_{r_info['node']}_{i}" # Key unique
            reaction_results[key] = {
                'node': r_info['node'],
                'magnitude': r_val,
                'angle_deg': r_info['angle']
            }
            
        return bar_results, reaction_results
        
    except np.linalg.LinAlgError:
        st.error("Ma trận suy biến. Hệ giàn không ổn định (biến hình). Kiểm tra lại liên kết.")
        return None, None