import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_single_bar(node1_name, node1_coord, node2_name, node2_coord, force):
    """
    Vẽ biểu đồ nội lực cho một thanh dưới dạng NẰM NGANG (Horizontal),
    bất kể vị trí thực tế của thanh trong không gian.
    """
    # 1. Tính độ dài thực tế của thanh
    p1_real = np.array(node1_coord)
    p2_real = np.array(node2_coord)
    length = np.linalg.norm(p2_real - p1_real)
    
    if length == 0: return None

    # 2. Thiết lập hệ tọa độ cục bộ (Local Coordinate) để vẽ nằm ngang
    # Đầu trái là (0,0), đầu phải là (Length, 0)
    x_start, y_start = 0, 0
    x_end, y_end = length, 0
    
    # 3. Thiết lập khung hình
    # Tỉ lệ khung hình dẹt (8x3) để phù hợp với thanh nằm ngang
    fig, ax = plt.subplots(figsize=(8, 3)) 
    ax.axis('off') # Tắt trục tọa độ
    
    # Vẽ trục thanh (đường tâm) nét đứt
    ax.plot([x_start, x_end], [y_start, y_end], 'k-.', lw=1, alpha=0.5)
    
    # 4. Vẽ biểu đồ lực (Hình chữ nhật)
    # Chiều cao biểu đồ: Tùy chọn khoảng 15% chiều dài thanh
    h_val = length * 0.15
    if h_val == 0: h_val = 0.5 # Fallback nếu thanh quá ngắn
    
    # Xác định màu sắc và chiều cao vẽ (trên hay dưới trục)
    # Quy ước thông thường: Dương (Kéo) vẽ bên trên, Âm (Nén) vẽ bên dưới (hoặc ngược lại tùy sách).
    # Ở đây ta vẽ Kéo (Dương) lên trên, Nén (Âm) xuống dưới cho trực quan.
    
    if force > 1e-5: # KÉO (+)
        color = 'blue'
        hatch = '|||' # Sọc dọc
        face_color = (0, 0, 1, 0.1)
        label_text = f"Lực Kéo (+): {abs(force):.2f} N"
        y_rect = h_val  # Vẽ lên trên
        
        # Tọa độ 4 góc hình chữ nhật
        poly_pts = [
            [x_start, y_start],
            [x_end, y_end],
            [x_end, y_rect],
            [x_start, y_rect]
        ]
        
    elif force < -1e-5: # NÉN (-)
        color = 'red'
        hatch = '///' # Sọc chéo
        face_color = (1, 0, 0, 0.1)
        label_text = f"Lực Nén (-): {abs(force):.2f} N"
        y_rect = -h_val # Vẽ xuống dưới
        
        # Tọa độ 4 góc hình chữ nhật
        poly_pts = [
            [x_start, y_start],
            [x_end, y_end],
            [x_end, y_rect],
            [x_start, y_rect]
        ]
        
    else: # Lực = 0
        color = 'gray'
        hatch = ''
        face_color = 'none'
        label_text = "Thanh không chịu lực (0 N)"
        poly_pts = []

    # Vẽ khối đa giác (Biểu đồ)
    if poly_pts:
        poly = mpatches.Polygon(poly_pts, closed=True, 
                                facecolor=face_color, edgecolor=color, hatch=hatch, alpha=0.9)
        ax.add_patch(poly)

    # 5. Vẽ 2 Nút ở hai đầu (Tròn đen)
    ax.plot(x_start, y_start, 'ko', markersize=8)
    ax.plot(x_end, y_end, 'ko', markersize=8)
    
    # Tên nút (Vẽ lùi ra ngoài một chút)
    ax.text(x_start - length*0.05, y_start, node1_name, ha='right', va='center', fontweight='bold', fontsize=12)
    ax.text(x_end + length*0.05, y_end, node2_name, ha='left', va='center', fontweight='bold', fontsize=12)

    # 6. Ghi giá trị lực ở giữa
    mid_x = length / 2
    if poly_pts:
        # Lấy toạ độ y giữa của hình chữ nhật để đặt text
        mid_y = y_rect / 2
        ax.text(mid_x, mid_y, f"{abs(force):.2f}", 
                color=color, fontweight='bold', ha='center', va='center', fontsize=11,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

    # 7. Tiêu đề & Căn chỉnh
    plt.title(f"Chi tiết Thanh {node1_name}-{node2_name} (Dài L={length:.2f}m)", fontsize=13)
    # Hiển thị trạng thái ở góc trên
    plt.text(mid_x, h_val * 1.5 if force >= 0 else h_val, label_text, 
             color=color, ha='center', fontweight='bold')

    # Zoom giới hạn trục để hình nằm giữa, chừa lề rộng rãi
    margin_x = length * 0.2
    margin_y = h_val * 1.8
    ax.set_xlim(x_start - margin_x, x_end + margin_x)
    ax.set_ylim(-margin_y, margin_y)
    
    plt.tight_layout()
    return fig