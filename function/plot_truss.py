import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import streamlit as st

def rotate_coords(x_arr, y_arr, cx, cy, angle_deg):
    """
    Xoay danh sách tọa độ (x_arr, y_arr) quanh tâm (cx, cy) một góc angle_deg.
    """
    rad = np.radians(angle_deg)
    c, s = np.cos(rad), np.sin(rad)
    
    # Chuyển về tọa độ cục bộ tương đối với tâm
    x_local = np.array(x_arr) - cx
    y_local = np.array(y_arr) - cy
    
    # Công thức xoay
    x_rot = cx + x_local * c - y_local * s
    y_rot = cy + x_local * s + y_local * c
    
    return x_rot, y_rot

def plot_truss(nodes, bars, bar_forces, supports, external_forces, reaction_results):
    """
    Vẽ hệ giàn với mũi tên lực có độ dài tỷ lệ với độ lớn.
    """
    
    # 1. TÍNH TOÁN TỶ LỆ KHUNG HÌNH
    all_coords = list(nodes.values())
    if not all_coords: all_coords = [[0, 0]]
    coords_np = np.array(all_coords)
    
    x_min, y_min = coords_np.min(axis=0)
    x_max, y_max = coords_np.max(axis=0)
    
    width_data = x_max - x_min
    height_data = y_max - y_min
    
    # Padding và Span
    span = max(width_data, height_data)
    if span == 0: span = 10
    padding = span * 0.2
    
    # Kích thước cơ sở (sz) dùng để vẽ gối, nút...
    sz = span * 0.04  
    
    # Thiết lập Figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_aspect('equal')

    # --- 2. VẼ THANH (BARS) & NỘI LỰC ---
    max_int_force = 1.0
    if bar_forces:
        vals = [abs(f) for f in bar_forces.values()]
        if vals: max_int_force = max(vals)
        if max_int_force == 0: max_int_force = 1.0

    for bar_nodes in bars:
        n1, n2 = bar_nodes
        if n1 not in nodes or n2 not in nodes: continue
            
        p1 = np.array(nodes[n1])
        p2 = np.array(nodes[n2])
        
        # Lấy giá trị lực
        key = f"S_{sorted(bar_nodes)[0]}-{sorted(bar_nodes)[1]}"
        force = bar_forces.get(key, 0.0)
        
        # Màu sắc
        if force > 1e-5: color = 'blue'    # Kéo
        elif force < -1e-5: color = 'red'  # Nén
        else: color = 'gray'               # Không lực
        
        # Độ đậm nét vẽ
        lw = 1.5 if abs(force) < 1e-5 else 1.5 + (abs(force)/max_int_force)*2.5
        
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=lw, zorder=1)
        
        # Hiển thị giá trị lực ở giữa thanh
        mid = (p1 + p2) / 2
        if abs(force) > 1e-5:
            ax.text(mid[0], mid[1], f"{force:.1f}", 
                    color=color, fontsize=9, fontweight='bold', ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

    # --- 3. VẼ NÚT (NODES) ---
    for name, (x, y) in nodes.items():
        ax.plot(x, y, 'ko', markersize=6, zorder=3)
        ax.text(x, y + sz*0.8, name, fontsize=11, ha='center', fontweight='bold', zorder=4)

    # --- 4. VẼ GỐI TỰA (SUPPORTS) ---
    for name, sup_data in supports.items():
        if name not in nodes: continue
        cx, cy = nodes[name]
        s_type = sup_data['type']
        angle = sup_data.get('angle', 0.0)
        
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
            # Gạch chéo
            for i in np.linspace(cx - 1.5*sz, cx + 1.5*sz, 7):
                h_x = [i, i - 0.3*sz]
                h_y = [cy - 1.5*sz, cy - 1.9*sz]
                rh_x, rh_y = rotate_coords(h_x, h_y, cx, cy, angle)
                ax.plot(rh_x, rh_y, 'k-', lw=1)
                
        elif s_type == 'roller':
            w1_x, w1_y = cx - 0.5*sz, cy - 1.8*sz
            w2_x, w2_y = cx + 0.5*sz, cy - 1.8*sz
            rw1_x, rw1_y = rotate_coords(w1_x, w1_y, cx, cy, angle)
            rw2_x, rw2_y = rotate_coords(w2_x, w2_y, cx, cy, angle)
            ax.plot(rw1_x, rw1_y, 'ko', markersize=4, zorder=2)
            ax.plot(rw2_x, rw2_y, 'ko', markersize=4, zorder=2)
            
            g_x = [cx - 1.5*sz, cx + 1.5*sz]
            g_y = [cy - 2.1*sz, cy - 2.1*sz]
            rg_x, rg_y = rotate_coords(g_x, g_y, cx, cy, angle)
            ax.plot(rg_x, rg_y, 'k-', lw=1.5, zorder=2)
            for i in np.linspace(cx - 1.5*sz, cx + 1.5*sz, 7):
                h_x = [i, i - 0.3*sz]
                h_y = [cy - 2.1*sz, cy - 2.5*sz]
                rh_x, rh_y = rotate_coords(h_x, h_y, cx, cy, angle)
                ax.plot(rh_x, rh_y, 'k-', lw=1)

    # --- 5. VẼ NGOẠI LỰC (EXTERNAL FORCES) - CÓ SCALE ĐỘ DÀI ---
    
    # B1: Tìm lực ngoại lực lớn nhất để làm chuẩn
    all_ext_mags = [np.sqrt(fx**2 + fy**2) for fx, fy in external_forces.values()]
    max_ext_force = max(all_ext_mags) if all_ext_mags else 1.0
    if max_ext_force == 0: max_ext_force = 1.0

    for name, (fx, fy) in external_forces.items():
        if name not in nodes or (fx==0 and fy==0): continue
        x, y = nodes[name]
        
        mag = np.sqrt(fx**2 + fy**2)
        
        # B2: Tính độ dài dựa trên tỷ lệ lực
        # Quy tắc: 
        # - Lực nhỏ nhất hiển thị = 1.5 * sz
        # - Lực lớn nhất hiển thị = 4.5 * sz
        # => arrow_len = sz * (1.5 + 3.0 * (mag / max_ext_force))
        
        ratio = mag / max_ext_force
        arrow_len = sz * (1.5 + 3.0 * ratio)
        
        # Vector đơn vị
        ux, uy = fx/mag, fy/mag
        
        # Đuôi mũi tên ở xa, đầu chạm vào nút
        tail_x = x - ux * arrow_len
        tail_y = y - uy * arrow_len
        
        ax.annotate("", xy=(x, y), xytext=(tail_x, tail_y),
                    arrowprops=dict(arrowstyle="->", color='#2ca02c', lw=2), zorder=5)
        
        # Hiển thị chữ F cách đuôi mũi tên một chút
        ax.text(tail_x, tail_y, f"F={mag:.1f}", color='#2ca02c', fontweight='bold', fontsize=10)

    # --- 6. VẼ PHẢN LỰC (REACTIONS) - CŨNG SCALE TƯƠNG TỰ ---
    
    # Tìm phản lực lớn nhất
    max_react_force = 1.0
    if reaction_results:
        r_mags = [r['magnitude'] for r in reaction_results.values()]
        if r_mags: max_react_force = max([abs(m) for m in r_mags])
    if max_react_force == 0: max_react_force = 1.0

    if reaction_results:
        for res in reaction_results.values():
            if res['node'] not in nodes: continue
            rx, ry = nodes[res['node']]
            mag = res['magnitude']
            ang = res['angle_deg']
            
            if abs(mag) < 1e-3: continue
            
            # Scale độ dài phản lực
            ratio = abs(mag) / max_react_force
            r_arrow_len = sz * (1.5 + 2.5 * ratio)
            
            rad = np.radians(ang)
            vx, vy = np.cos(rad), np.sin(rad)
            
            if mag < 0:
                vx, vy = -vx, -vy
                mag = -mag
            
            ax.arrow(rx, ry, vx*r_arrow_len, vy*r_arrow_len,
                     head_width=sz*0.4, fc='#9467bd', ec='#9467bd', lw=1.5, zorder=4, linestyle='--')
            
            ax.text(rx + vx*r_arrow_len*1.1, ry + vy*r_arrow_len*1.1, f"{mag:.1f}", color='#9467bd', fontsize=9)

    # --- 7. HOÀN THIỆN ---
    patches = [
        mpatches.Patch(color='blue', label='Thanh chịu Kéo (+)'),
        mpatches.Patch(color='red', label='Thanh chịu Nén (-)'),
        mpatches.Patch(color='#2ca02c', label='Ngoại lực (F)'),
        mpatches.Patch(color='#9467bd', label='Phản lực (R)')
    ]
    ax.legend(handles=patches, loc='lower right', fontsize='small')
    
    ax.set_xlim(x_min - padding, x_max + padding)
    ax.set_ylim(y_min - padding, y_max + padding)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig