import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ==========================================
# 1. HÀM HỖ TRỢ (Copy từ các bước trước)
# ==========================================

def rotate_coords(x_arr, y_arr, cx, cy, angle_deg):
    rad = np.radians(angle_deg)
    c, s = np.cos(rad), np.sin(rad)
    x_local = np.array(x_arr) - cx
    y_local = np.array(y_arr) - cy
    x_rot = cx + x_local * c - y_local * s
    y_rot = cy + x_local * s + y_local * c
    return x_rot, y_rot

def plot_truss_sim(nodes, bars, bar_forces, supports, external_forces, reaction_results):
    """Vẽ cấu trúc hình học và gối tựa"""
    all_coords = list(nodes.values())
    coords_np = np.array(all_coords)
    x_min, y_min = coords_np.min(axis=0)
    x_max, y_max = coords_np.max(axis=0)
    
    width_data = x_max - x_min
    height_data = y_max - y_min
    span = max(width_data, height_data) if max(width_data, height_data) > 0 else 10
    padding = span * 0.2
    sz = span * 0.05 

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_aspect('equal')

    # Vẽ thanh
    for bar in bars:
        n1, n2 = bar
        p1, p2 = np.array(nodes[n1]), np.array(nodes[n2])
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='gray', linewidth=2, zorder=1)

    # Vẽ nút
    for name, (x, y) in nodes.items():
        ax.plot(x, y, 'ko', markersize=6, zorder=3)
        ax.text(x, y + sz*0.8, name, fontsize=12, fontweight='bold', ha='center')

    # Vẽ gối tựa (Supports) - CÓ XOAY
    for name, sup in supports.items():
        cx, cy = nodes[name]
        s_type = sup['type']
        angle = sup.get('angle', 0)
        
        # Tam giác cơ bản
        tri_x = [cx, cx - sz, cx + sz, cx]
        tri_y = [cy, cy - 1.5*sz, cy - 1.5*sz, cy]
        rx, ry = rotate_coords(tri_x, tri_y, cx, cy, angle)
        ax.plot(rx, ry, 'k-', lw=1.5, zorder=2)

        if s_type == 'pin':
            g_x = [cx - 1.5*sz, cx + 1.5*sz]
            g_y = [cy - 1.5*sz, cy - 1.5*sz]
            rg_x, rg_y = rotate_coords(g_x, g_y, cx, cy, angle)
            ax.plot(rg_x, rg_y, 'k-', lw=1.5, zorder=2)
            # Hatching
            for i in np.linspace(cx - 1.5*sz, cx + 1.5*sz, 6):
                h_x, h_y = [i, i-0.3*sz], [cy-1.5*sz, cy-1.9*sz]
                rh_x, rh_y = rotate_coords(h_x, h_y, cx, cy, angle)
                ax.plot(rh_x, rh_y, 'k-', lw=1)
                
        elif s_type == 'roller':
            # Bánh xe
            w1_x, w1_y = cx - 0.5*sz, cy - 1.8*sz
            w2_x, w2_y = cx + 0.5*sz, cy - 1.8*sz
            rw1_x, rw1_y = rotate_coords(w1_x, w1_y, cx, cy, angle)
            rw2_x, rw2_y = rotate_coords(w2_x, w2_y, cx, cy, angle)
            ax.plot(rw1_x, rw1_y, 'ko', markersize=4, zorder=2)
            ax.plot(rw2_x, rw2_y, 'ko', markersize=4, zorder=2)
            # Đất
            g_x, g_y = [cx - 1.5*sz, cx + 1.5*sz], [cy - 2.1*sz, cy - 2.1*sz]
            rg_x, rg_y = rotate_coords(g_x, g_y, cx, cy, angle)
            ax.plot(rg_x, rg_y, 'k-', lw=1.5, zorder=2)

    # Vẽ ngoại lực
    for name, (fx, fy) in external_forces.items():
        if fx == 0 and fy == 0: continue
        x, y = nodes[name]
        ax.annotate("", xy=(x, y), xytext=(x, y + sz*3),
                    arrowprops=dict(arrowstyle="->", color='green', lw=3), zorder=5)
        ax.text(x, y + sz*3.2, "P=10kN", color='green', ha='center')

    # Vẽ phản lực (Reactions)
    for res in reaction_results.values():
        rx, ry = nodes[res['node']]
        mag = res['magnitude']
        # Đơn giản hóa vẽ phản lực cho demo
        ax.text(rx, ry - sz*3, f"R={mag}", color='purple', ha='center')
        ax.arrow(rx, ry - sz*2.5, 0, sz*2, head_width=sz*0.3, color='purple')

    ax.set_title("HÌNH 1: CẤU TRÚC HÌNH HỌC (Gối xoay 30 độ)", fontsize=14)
    ax.axis('equal')
    ax.grid(True, linestyle=':', alpha=0.5)
    return fig

def plot_force_diagram_sim(nodes, bars, bar_forces):
    """Vẽ biểu đồ nội lực (Kéo/Nén)"""
    all_coords = list(nodes.values())
    coords_np = np.array(all_coords)
    span = 4 # Hardcode cho demo
    sz = span * 0.04
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_aspect('equal')
    ax.axis('off') # Tắt trục
    
    max_force = max([abs(f) for f in bar_forces.values()])

    for bar in bars:
        n1, n2 = bar
        p1, p2 = np.array(nodes[n1]), np.array(nodes[n2])
        vec = p2 - p1
        length = np.linalg.norm(vec)
        
        key = f"S_{min(n1,n2)}-{max(n1,n2)}"
        force = bar_forces.get(key, 0)
        abs_force = abs(force)

        # Màu sắc
        if force > 0: color, label_c = '#1f77b4', 'blue' # Kéo
        elif force < 0: color, label_c = '#d62728', 'red' # Nén
        else: color, label_c = 'gray', 'gray'
        
        lw = 2 + (abs_force/max_force)*6
        
        # Vẽ thanh
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=lw, alpha=0.9)
        
        # Mũi tên nội lực
        mid = (p1 + p2) / 2
        uv = vec / length
        offset = uv * (sz * 2)
        arrow_sz = sz * 0.8
        
        if force > 0: # Kéo: Mũi tên hướng ra xa <-- -->
             ax.arrow(*(mid-offset), *(-uv*arrow_sz), head_width=sz*0.5, color=color)
             ax.arrow(*(mid+offset), *(uv*arrow_sz), head_width=sz*0.5, color=color)
        elif force < 0: # Nén: Mũi tên hướng vào nhau --> <--
             ax.arrow(*(mid-offset-uv*arrow_sz), *(uv*arrow_sz), head_width=sz*0.5, color=color)
             ax.arrow(*(mid+offset+uv*arrow_sz), *(-uv*arrow_sz), head_width=sz*0.5, color=color)

        # Text giá trị
        ax.text(mid[0], mid[1], f"{abs(force)}", color=label_c, fontweight='bold',
                bbox=dict(boxstyle="round", fc='white', ec='none', alpha=0.8))

    # Vẽ nút mờ
    for x, y in nodes.values():
        ax.plot(x, y, 'ko', alpha=0.3, markersize=4)

    # Legend
    p = [mpatches.Patch(color='#1f77b4', label='Kéo (+)'), mpatches.Patch(color='#d62728', label='Nén (-)')]
    ax.legend(handles=p, loc='upper right')
    ax.set_title("HÌNH 2: BIỂU ĐỒ NỘI LỰC (Ứng suất)", fontsize=14)
    return fig

# ==========================================
# 2. DỮ LIỆU MẪU (Giàn tam giác đơn giản)
# ==========================================
# Nút: A(0,0), B(4,0), C(2,3)
nodes = {
    'A': [0, 0],
    'B': [4, 0], # Gối nghiêng ở đây
    'C': [2, 3.464] # Tam giác đều cạnh 4
}

# Thanh: AC, BC, AB
bars = [('A', 'C'), ('B', 'C'), ('A', 'B')]

# Gối tựa: A (Pin), B (Roller xoay 30 độ)
supports = {
    'A': {'type': 'pin', 'angle': 0},
    'B': {'type': 'roller', 'angle': 30} # <--- TEST GÓC XOAY TẠI ĐÂY
}

# Ngoại lực: Tại C, lực nén xuống 10kN
external_forces = { 'C': (0, -10) }

# Kết quả giả định (để test vẽ)
# Thanh xiên chịu nén, thanh ngang chịu kéo
bar_forces = {
    'S_A-C': -5.77, # Nén
    'S_B-C': -5.77, # Nén
    'S_A-B': 2.89   # Kéo
}

reaction_results = {
    'R_A': {'node': 'A', 'magnitude': 5.0, 'angle_deg': 90},
    'R_B': {'node': 'B', 'magnitude': 5.0, 'angle_deg': 90}
}

# ==========================================
# 3. CHẠY VẼ
# ==========================================
print("Đang tạo hình ảnh mô phỏng...")

# Hình 1: Cấu trúc
fig1 = plot_truss_sim(nodes, bars, bar_forces, supports, external_forces, reaction_results)

# Hình 2: Nội lực
fig2 = plot_force_diagram_sim(nodes, bars, bar_forces)

plt.show()