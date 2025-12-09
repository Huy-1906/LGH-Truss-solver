import os
import sys
# Thêm thư mục hiện tại vào đường dẫn để import các module trong folder function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Import các hàm xử lý từ thư mục function
from function.solve_general_truss import solve_general_truss
from function.calculate_bar_properties import calculate_bar_properties
from function.plot_truss import plot_truss
from function.plot_single_bar import plot_single_bar  # Đảm bảo bạn đã có file này

def main():
    st.set_page_config(layout="wide", page_title="Chương trình Tính toán Hệ Giàn")
    
    st.title("Chương trình xác định ứng lực các thanh trong hệ giàn 2D & Vẽ sơ đồ Ứng lực")
    st.markdown("---")

    # --- 1. KHỞI TẠO SESSION STATE ---
    if 'nodes' not in st.session_state:
        st.session_state.nodes = {}          
    if 'bars' not in st.session_state:
        st.session_state.bars = []           
    if 'supports' not in st.session_state:
        st.session_state.supports = {}       
    if 'external_forces' not in st.session_state:
        st.session_state.external_forces = {} 
    if 'bar_results' not in st.session_state:
        st.session_state.bar_results = {}
    if 'reaction_results' not in st.session_state:
        st.session_state.reaction_results = {}

    all_nodes = list(st.session_state.nodes.keys())

    # --- 2. THANH SIDEBAR (NHẬP LIỆU) ---
    st.sidebar.header("Công cụ Thiết kế")

    # --- A. QUẢN LÝ NÚT (NODES) ---
    with st.sidebar.expander("1. Thêm/Xóa Nút (Nodes)", expanded=True):
        with st.form("add_node_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([1, 1, 1])
            name = col1.text_input("Tên", "A")
            nx = col2.number_input("X (m)", value=0.0, step=0.5)
            ny = col3.number_input("Y (m)", value=0.0, step=0.5)
            
            if st.form_submit_button("Thêm Nút"):
                if not name:
                    st.error("Tên nút không được để trống")
                elif name in st.session_state.nodes:
                    st.error("Nút đã tồn tại")
                else:
                    st.session_state.nodes[name] = [nx, ny]
                    st.success(f"Đã thêm nút {name}")
                    st.rerun()
        
        if all_nodes:
            del_node = st.selectbox("Chọn nút cần xóa", [""] + all_nodes, key="del_node_box")
            if del_node and st.button("Xóa Nút"):
                del st.session_state.nodes[del_node]
                st.session_state.bars = [b for b in st.session_state.bars if del_node not in b]
                if del_node in st.session_state.supports: del st.session_state.supports[del_node]
                if del_node in st.session_state.external_forces: del st.session_state.external_forces[del_node]
                st.session_state.bar_results = {}
                st.session_state.reaction_results = {}
                st.rerun()

    # --- B. QUẢN LÝ THANH (BARS) ---
    with st.sidebar.expander("2. Thêm/Xóa Thanh (Bars)"):
        if len(all_nodes) >= 2:
            with st.form("add_bar_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                b1 = col1.selectbox("Nút đầu", all_nodes, key="b1")
                b2 = col2.selectbox("Nút cuối", all_nodes, index=1 if len(all_nodes)>1 else 0, key="b2")
                
                if st.form_submit_button("Thêm Thanh"):
                    if b1 == b2:
                        st.error("Hai đầu thanh phải khác nhau.")
                    else:
                        new_bar = tuple(sorted((b1, b2)))
                        if new_bar in st.session_state.bars:
                            st.warning("Thanh này đã tồn tại.")
                        else:
                            st.session_state.bars.append(new_bar)
                            st.success(f"Đã nối {b1}-{b2}")
                            st.rerun()
            
            if st.session_state.bars:
                st.write(f"Tổng số thanh: {len(st.session_state.bars)}")
                if st.button("Xóa thanh vừa thêm"):
                    st.session_state.bars.pop()
                    st.rerun()
        else:
            st.info("Cần ít nhất 2 nút để tạo thanh.")

    # --- C. QUẢN LÝ GỐI TỰA (SUPPORTS) ---
    with st.sidebar.expander("3. Gối tựa (Supports)", expanded=True):
        if all_nodes:
            with st.form("support_form"):
                s_node = st.selectbox("Chọn nút đặt gối", all_nodes)
                col_type, col_angle = st.columns(2)
                s_type = col_type.selectbox("Loại gối", ["pin", "roller"], format_func=lambda x: "Gối cố định (Pin)" if x == "pin" else "Gối di động (Roller)")
                s_angle = col_angle.number_input("Góc xoay (°)", value=0.0, step=15.0, help="0°: Nằm ngang, 90°: Thẳng đứng")
                
                if st.form_submit_button("Đặt / Cập nhật Gối"):
                    st.session_state.supports[s_node] = {'type': s_type, 'angle': s_angle}
                    st.success(f"Đã đặt gối tại {s_node}")
                    st.rerun()
            
            if st.session_state.supports:
                st.markdown("**Các gối hiện tại:**")
                for n, s in st.session_state.supports.items():
                    t_name = "Cố định" if s['type'] == 'pin' else "Di động"
                    st.caption(f"- **{n}**: {t_name} ({s['angle']}°)")
                
                rem_sup = st.selectbox("Xóa gối tại nút", [""] + list(st.session_state.supports.keys()))
                if rem_sup and st.button("Xóa Gối"):
                    del st.session_state.supports[rem_sup]
                    st.rerun()
        else:
            st.info("Chưa có nút nào.")

    # --- D. QUẢN LÝ NGOẠI LỰC (FORCES) ---
    with st.sidebar.expander("4. Ngoại lực (External Forces)"):
        if all_nodes:
            with st.form("force_form"):
                f_node = st.selectbox("Nút chịu lực", all_nodes)
                col_mag, col_ang = st.columns(2)
                mag = col_mag.number_input("Độ lớn (N)", value=1000.0, step=100.0)
                ang = col_ang.number_input("Góc (°)", value=-90.0, step=15.0, help="So với trục Ox dương")
                
                if st.form_submit_button("Thêm Lực"):
                    rad = np.radians(ang)
                    fx = mag * np.cos(rad)
                    fy = mag * np.sin(rad)
                    st.session_state.external_forces[f_node] = [fx, fy]
                    st.success(f"Đã thêm lực vào {f_node}")
                    st.rerun()
            
            if st.session_state.external_forces:
                st.markdown("**Lực đang tác dụng:**")
                nodes_with_force = list(st.session_state.external_forces.keys())
                for n in nodes_with_force:
                    fx, fy = st.session_state.external_forces[n]
                    F = np.sqrt(fx**2 + fy**2)
                    st.caption(f"- **{n}**: F={F:.1f}N (Fx={fx:.1f}, Fy={fy:.1f})")
                
                rem_force = st.selectbox("Xóa lực tại", [""] + nodes_with_force)
                if rem_force and st.button("Xóa Lực"):
                    del st.session_state.external_forces[rem_force]
                    st.rerun()

    # --- ACTIONS ---
    st.sidebar.markdown("---")
    col_act1, col_act2 = st.sidebar.columns(2)
    
    solve_clicked = col_act1.button("Giải hệ", type="primary", use_container_width=True)
    reset_clicked = col_act2.button("Xóa hết", use_container_width=True)

    if solve_clicked:
        if not st.session_state.nodes or not st.session_state.bars or not st.session_state.supports:
            st.error("Hệ chưa đủ điều kiện để giải (cần Nút, Thanh và Gối).")
        else:
            with st.spinner("Đang tính toán ma trận..."):
                b_res, r_res = solve_general_truss(
                    st.session_state.nodes,
                    st.session_state.bars,
                    st.session_state.supports,
                    st.session_state.external_forces
                )
                if b_res is not None:
                    st.session_state.bar_results = b_res
                    st.session_state.reaction_results = r_res
                    st.success("Tính toán hoàn tất!")
                else:
                    st.session_state.bar_results = {}
                    st.session_state.reaction_results = {}

    if reset_clicked:
        st.session_state.nodes = {}
        st.session_state.bars = []
        st.session_state.supports = {}
        st.session_state.external_forces = {}
        st.session_state.bar_results = {}
        st.session_state.reaction_results = {}
        st.rerun()

    # --- 3. KHU VỰC HIỂN THỊ CHÍNH (RESPONSIVE LAYOUT) ---
    col_main, col_info = st.columns([0.65, 0.35])

    # --- CỘT TRÁI: SƠ ĐỒ TỔNG THỂ ---
    with col_main:
        st.subheader("Sơ đồ tính toán các ứng lực trên hệ giàn 2D")
        
        if st.session_state.nodes:
            fig = plot_truss(
                st.session_state.nodes,
                st.session_state.bars,
                st.session_state.bar_results,
                st.session_state.supports,
                st.session_state.external_forces,
                st.session_state.reaction_results
            )
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Vui lòng sử dụng thanh bên trái để thêm Nút, Thanh và Gối tựa.")
            st.empty()

    # --- CỘT PHẢI: KẾT QUẢ & CHI TIẾT ---
    with col_info:
        st.subheader("Kết quả Phân tích")
        
        tab1, tab2 = st.tabs(["Kết quả Tính toán", "Dữ liệu Đầu vào"])
        
        with tab1:
            if st.session_state.bar_results:
                
                # --- CHỌN THANH & VẼ BIỂU ĐỒ NỘI LỰC ---
                st.markdown("#### Sơ đồ ứng lực")
                st.caption("Chọn thanh bên dưới để xem chi tiết:")
                
                # Tạo list tên thanh hiển thị
                bar_options = [f"{b[0]}-{b[1]}" for b in st.session_state.bars]
                selected_bar_str = st.selectbox("Chọn thanh:", bar_options, label_visibility="collapsed")
                
                if selected_bar_str:
                    # Lấy thông tin thanh được chọn
                    n1_name, n2_name = selected_bar_str.split('-')
                    # Tìm key lực trong kết quả (Key được lưu dạng sorted)
                    key_sorted = f"S_{sorted((n1_name, n2_name))[0]}-{sorted((n1_name, n2_name))[1]}"
                    force_val = st.session_state.bar_results.get(key_sorted, 0.0)
                    
                    coord1 = st.session_state.nodes[n1_name]
                    coord2 = st.session_state.nodes[n2_name]
                    
                    # Gọi hàm vẽ chi tiết
                    fig_detail = plot_single_bar(n1_name, coord1, n2_name, coord2, force_val)
                    if fig_detail:
                        st.pyplot(fig_detail, use_container_width=True)

                st.divider()

                # --- DANH SÁCH TẤT CẢ CÁC THANH ---
                st.markdown("##### Danh sách Nội lực toàn hệ")
                for bar_name, force in st.session_state.bar_results.items():
                    if force > 1e-5:
                        color = "blue"
                        status = "Kéo"
                    elif force < -1e-5:
                        color = "red"
                        status = "Nén"
                    else:
                        color = "grey"
                        status = "Không chịu lực"
                    
                    # Hiển thị gọn hơn
                    st.markdown(f"**{bar_name}**: :{color}[**{force:.2f} N**] ({status})")
                
                st.divider()
                st.markdown("##### Phản lực liên kết")
                for r_name, r_val in st.session_state.reaction_results.items():
                    node = r_val['node']
                    mag = r_val['magnitude']
                    ang = r_val['angle_deg']
                    st.markdown(f"- **{node}**: {mag:.2f} N (Hướng {ang}°)")
            
            else:
                st.info("Chưa có kết quả. Hãy bấm nút 'GIẢI HỆ'.")

        with tab2:
            with st.expander("Danh sách Nút"):
                st.json(st.session_state.nodes)
            with st.expander("Danh sách Thanh"):
                st.write(st.session_state.bars)
            with st.expander("Gối tựa"):
                st.json(st.session_state.supports)
            with st.expander("Ngoại lực"):
                st.json(st.session_state.external_forces)

if __name__ == "__main__":
    main()