def plot_truss(nodes, bars, bar_forces, supports, external_forces, reaction_results):
    """Vẽ hệ giàn một cách tổng quát."""
    
    fig, ax = plt.subplots(figsize=(12, 8))

    # 1. Vẽ các thanh (Bars)
    if bar_forces:
        forces_list = np.array(list(bar_forces.values()))
        max_abs_force = np.max(np.abs(forces_list))
        if max_abs_force == 0: max_abs_force = 1
    else:
        forces_list = []
        max_abs_force = 1

    for i, bar_nodes in enumerate(bars):
        n1, n2 = bar_nodes
        
        if n1 not in nodes or n2 not in nodes:
            st.warning(f"Bỏ qua vẽ thanh ({n1}, {n2}) vì một trong các nút đã bị xóa.")
            continue
            
        coord1, coord2 = nodes[n1], nodes[n2]
        x_vals, y_vals = [coord1[0], coord2[0]], [coord1[1], coord2[1]]
        
        n1_sorted, n2_sorted = tuple(sorted(bar_nodes))
        force_name = f"S_{n1_sorted}-{n2_sorted}"
        force = bar_forces.get(force_name, 0)
        
        if force > 1e-6: color = 'blue'
        elif force < -1e-6: color = 'red'
        else: color = 'gray'
            
        linewidth = 1 + np.abs(force) / max_abs_force * 4
        
        ax.plot(x_vals, y_vals, color=color, linewidth=linewidth, zorder=1)
        
        mid_x, mid_y = (x_vals[0] + x_vals[1]) / 2, (y_vals[0] + y_vals[1]) / 2
        ax.text(mid_x, mid_y, f"{force:.1f}", 
                 fontsize=10, color='black', ha='center', va='center',
                 bbox=dict(facecolor='white', alpha=0.7, pad=0.1))

    # 2. Vẽ các nút (Nodes)
    all_coords = list(nodes.values())
    if not all_coords: 
        all_coords = [[0, 0]]
        
    max_coord_val = np.max(np.abs(all_coords))
    min_coord_val = np.min(all_coords)
    # Tính kích thước dựa trên đường chéo của bounding box
    span = max_coord_val - min_coord_val
    support_size = span * 0.05 
    if support_size == 0: support_size = 0.5 
    
    for name, (x, y) in nodes.items():
        ax.plot(x, y, 'ko', markersize=10, zorder=2)
        ax.text(x, y + support_size*0.5, name, fontsize=16, ha='center', va='bottom', weight='bold')

    # 3. Vẽ các gối tựa (Supports)
    for name, type in supports.items():
        if name not in nodes:
            st.warning(f"Bỏ qua vẽ gối tựa tại '{name}' vì nút đã bị xóa.")
            continue
            
        x, y = nodes[name]
        
        if type == 'pin':
            # Vẽ gối cố định (tam giác + đất)
            tri_x = [x, x - support_size, x + support_size, x]
            tri_y = [y, y - support_size*1.5, y - support_size*1.5, y]
            ax.plot(tri_x, tri_y, 'k-', lw=2)
            
            ground_x = [x - support_size*1.3, x + support_size*1.3]
            ground_y = [y - support_size*1.5, y - support_size*1.5]
            ax.plot(ground_x, ground_y, 'k-', lw=2)
            
            # Đã sửa lỗi (thêm dấu [ ] cho y)
            for x_hatch in np.linspace(ground_x[0], ground_x[1], 7):
                ax.plot([x_hatch, x_hatch - 0.2*support_size], 
                        [ground_y[0], ground_y[0] - 0.4*support_size], 'k-', lw=1)

        elif type == 'roller_y':
            # Vẽ gối di động Y (tam giác + bánh xe + đất)
            tri_x = [x, x - support_size, x + support_size, x]
            tri_y = [y, y - support_size*1.5, y - support_size*1.5, y]
            ax.plot(tri_x, tri_y, 'k-', lw=2)
            
            # Đã sửa lỗi (cần 2 tọa độ y)
            ax.scatter([x - support_size/2, x + support_size/2], 
                       [y - support_size*1.8, y - support_size*1.8], c='k', s=50, zorder=3)
            
            # Đã sửa lỗi (thêm 1 giá trị y)
            ax.plot([x - support_size*1.3, x + support_size*1.3], 
                    [y - support_size*2.0, y - support_size*2.0], 'k-', lw=2)

        elif type == 'roller_x':
            # Vẽ gối di động X (tam giác xoay 90 độ + bánh xe + tường)
            tri_x = [x, x - support_size*1.5, x - support_size*1.5, x]
            tri_y = [y, y - support_size, y + support_size, y]
            ax.plot(tri_x, tri_y, 'k-', lw=2)
            
            # Bánh xe
            ax.scatter([x - support_size*1.8, x - support_size*1.8], 
                       [y - support_size/2, y + support_size/2], c='k', s=50, zorder=3)
            
            # Tường
            wall_x_coord = x - support_size*2.0
            wall_y_range = [y - support_size*1.3, y + support_size*1.3]
            ax.plot([wall_x_coord, wall_x_coord], wall_y_range, 'k-', lw=2) # Đã sửa lỗi
            
            # Thêm gạch (hatching) cho tường
            for y_hatch in np.linspace(wall_y_range[0], wall_y_range[1], 7):
                ax.plot([wall_x_coord, wall_x_coord - 0.4*support_size], # x, x'
                        [y_hatch, y_hatch - 0.2*support_size],    # y, y'
                        'k-', lw=1)
            
    # 4. Vẽ ngoại lực (External Forces)
    force_scale = support_size * 4 
    
    for name, (fx, fy) in external_forces.items():
        if name not in nodes:
            st.warning(f"Bỏ qua vẽ lực tại '{name}' vì nút đã bị xóa.")
            continue
            
        if fx == 0 and fy == 0: continue
        x, y = nodes[name]
        
        mag = np.sqrt(fx**2 + fy**2)
        if mag == 0: continue
            
        angle_rad = np.arctan2(fy, fx)
        c, s = np.cos(angle_rad), np.sin(angle_rad)

        arrow_len = force_scale
        start_x = x - c * arrow_len
        start_y = y - s * arrow_len
        dx, dy = c * (arrow_len - support_size*0.5), s * (arrow_len - support_size*0.5) 
        
        if dx != 0 or dy != 0:
            ax.arrow(start_x, start_y, dx, dy, 
                     head_width=support_size*0.6, head_length=support_size*0.8, 
                     fc='green', ec='green', width=support_size*0.1, zorder=4)
            ax.text(start_x, start_y, f"F (tại {name})", 
                    fontsize=12, color='green', ha='center', va='center')

    # 5. Vẽ phản lực (Reactions)
    if reaction_results:
        for name, force in reaction_results.items():
            _, r_node, r_dir = name.split('_')
            
            if r_node not in nodes:
                continue 
                
            x, y = nodes[r_node]
            if abs(force) < 1e-6: continue
            
            mag = abs(force)
            if r_dir == 'x':
                c, s = 1.0 * (force/mag), 0.0
            else: # r_dir == 'y'
                c, s = 0.0, 1.0 * (force/mag)

            start_x, start_y = x - c * force_scale, y - s * force_scale
            dx, dy = c * (force_scale - support_size*0.5), s * (force_scale - support_size*0.5)

            if dx != 0 or dy != 0:
                ax.arrow(start_x, start_y, dx, dy, 
                         head_width=support_size*0.6, head_length=support_size*0.8, 
                         fc='purple', ec='purple', width=support_size*0.1, zorder=4)
                ax.text(start_x - c*support_size*0.3, start_y - s*support_size*0.3, 
                        f"{force:.1f}", color='purple', ha='center', va='center')

    # 6. Tinh chỉnh và HIỂN THỊ
    ax.set_title("Kết quả Phân tích Hệ Giàn", fontsize=18)
    red_patch = mpatches.Patch(color='red', label='Nén (Compression)')
    blue_patch = mpatches.Patch(color='blue', label='Kéo (Tension)')
    gray_patch = mpatches.Patch(color='gray', label='Lực ~ 0')
    ax.legend(handles=[red_patch, blue_patch, gray_patch], loc='lower right')
    ax.axis('equal')
    ax.grid(True, linestyle='--', alpha=0.6)
    return fig
