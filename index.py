#.....................................................................
# Code chương trình giải bài toán hệ giàn 2D tổng quát 
# 2452391 - Ly Gia Huy
#.....................................................................
# thêm các thư viện cần thiết
import sys
sys.path.insert(0,'/function') # thêm đường dẫn đến các hàm (Tùy vào máy mà sẽ đường dẫn sẽ khác nhau)

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from function.solve_general_truss import solve_general_truss
from function.calculate_bar_properties import calculate_bar_properties
from function.plot_truss import plot_truss
def main():
    st.set_page_config(layout="wide")
    st.title("Chương trình giải Hệ Giàn Phẳng 2D Tương Tác")
    st.write("Xây dựng hệ giàn bằng cách thêm Nút, Thanh, Gối tựa và Nội lực tác dụng.")

    # --- KHỞI TẠO BIẾN TRẠNG THÁI (SESSION STATE) ---
    if 'nodes' not in st.session_state:
        # Khởi tạo rỗng
        st.session_state.nodes = {}
        st.session_state.bars = []
        st.session_state.supports = {}
        st.session_state.external_forces = {}
        st.session_state.bar_results = {}
        st.session_state.reaction_results = {}

    # --- THANH BÊN (SIDEBAR) ĐỂ NHẬP LIỆU ---
    st.sidebar.title("Thiết lập Hệ Giàn")

    # --- Quay lại st.number_input ---
    with st.sidebar.expander("1. Thêm/Xóa Nút (Nodes)", expanded=True):
        with st.form("node_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            node_name = col1.text_input("Tên Nút", "A")
            
            # Quay lại dùng number_input
            node_x = col2.number_input("Tọa độ X", value=0.0, format="%.2f")
            node_y = col3.number_input("Tọa độ Y", value=0.0, format="%.2f")
            
            if st.form_submit_button("Thêm Nút"):
                if node_name.strip() == "":
                    st.error("Tên nút không được để trống.")
                elif node_name in st.session_state.nodes:
                    st.error(f"Nút '{node_name}' đã tồn tại.")
                else:
                    # Lưu tọa độ trực tiếp
                    st.session_state.nodes[node_name] = [node_x, node_y]
                    st.success(f"Đã thêm nút {node_name} ({node_x:.2f}, {node_y:.2f}).")
                    st.rerun()

        # Phần xóa nút
        node_options = list(st.session_state.nodes.keys())
        del_node = st.selectbox("Chọn nút để xóa", options=[""] + node_options)
        if del_node and st.button(f"Xóa nút {del_node}"):
            del st.session_state.nodes[del_node]
            # Tự động xóa các thanh, gối, lực liên quan
            st.session_state.bars = [b for b in st.session_state.bars if del_node not in b]
            if del_node in st.session_state.supports: del st.session_state.supports[del_node]
            if del_node in st.session_state.external_forces: del st.session_state.external_forces[del_node]
            # Xóa kết quả cũ
            st.session_state.bar_results = {}
            st.session_state.reaction_results = {}
            st.rerun()

    # Thanh (Bars)
    with st.sidebar.expander("2. Thêm/Xóa Thanh (Bars)"):
        if len(node_options) >= 2:
            with st.form("bar_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                bar_n1 = col1.selectbox("Nút 1", node_options, index=0)
                bar_n2 = col2.selectbox("Nút 2", node_options, index=1)
                
                if st.form_submit_button("Thêm Thanh"):
                    bar_tuple = tuple(sorted((bar_n1, bar_n2)))
                    if bar_n1 == bar_n2:
                        st.error("Không thể tạo thanh nối 1 nút.")
                    elif bar_tuple in st.session_state.bars:
                        st.error(f"Thanh {bar_tuple} đã tồn tại.")
                    else:
                        st.session_state.bars.append(bar_tuple)
                        st.success(f"Đã thêm thanh {bar_tuple}.")
                        st.rerun()
        else:
            st.warning("Cần ít nhất 2 nút để thêm thanh.")

    # Gối tựa (Supports)
    with st.sidebar.expander("3. Thêm Gối tựa (Supports)"):
        if node_options:
            with st.form("support_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                support_node = col1.selectbox("Chọn Nút", node_options)
                support_type = col2.selectbox("Loại gối tựa", ['pin', 'roller_y', 'roller_x'])
                
                if st.form_submit_button("Đặt/Cập nhật Gối tựa"):
                    st.session_state.supports[support_node] = support_type
                    st.success(f"Đã đặt gối {support_type} tại {support_node}.")
                    st.rerun()
        else:
            st.warning("Cần thêm nút trước.")

    # Nhập Lực (theo Góc hoặc Fx, Fy)
    with st.sidebar.expander("4. Thêm Lực (External Forces)"):
        if node_options:
            force_node = st.selectbox("Chọn Nút đặt lực", node_options, key="force_node_select")
            
            # Chọn kiểu nhập
            input_type = st.radio("Chọn kiểu nhập lực", 
                                  ["Theo Thành phần (Fx, Fy)", "Theo Độ lớn và Góc"])
            
            with st.form("force_form", clear_on_submit=False):
                fx, fy = 0.0, 0.0
                
                if input_type == "Theo Thành phần (Fx, Fy)":
                    col1, col2 = st.columns(2)
                    fx = col1.number_input("Lực Fx", value=0.0, format="%.2f")
                    fy = col2.number_input("Lực Fy", value=0.0, format="%.2f")
                
                else: # Theo Độ lớn và Góc
                    col1, col2 = st.columns(2)
                    mag = col1.number_input("Độ lớn (Magnitude)", value=1000.0, format="%.2f")
                    # Góc 0 độ là Ox, 90 độ là Oy (theo chuẩn toán học)
                    angle = col2.number_input("Góc (so với Ox, độ)", value=-90.0, format="%.2f") 
                    
                    # Tự động tính Fx, Fy
                    angle_rad = np.radians(angle)
                    fx = mag * np.cos(angle_rad)
                    fy = mag * np.sin(angle_rad)
                    st.info(f"Đã tính: Fx = {fx:.2f}, Fy = {fy:.2f}")

                if st.form_submit_button("Đặt/Cập nhật Lực"):
                    if fx == 0 and fy == 0:
                        if force_node in st.session_state.external_forces:
                            del st.session_state.external_forces[force_node]
                            st.info(f"Đã xóa lực tại {force_node}.")
                    else:
                        st.session_state.external_forces[force_node] = [fx, fy]
                        st.success(f"Đã đặt lực ({fx:.2f}, {fy:.2f}) tại {force_node}.")
                    st.rerun()
        else:
            st.warning("Cần thêm nút trước.")

    # Nút điều khiển
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    
    if col1.button("Giải Hệ Giàn", type="primary", use_container_width=True):
        if not st.session_state.nodes or not st.session_state.bars or not st.session_state.supports:
             st.error("Cần có ít nhất 1 Nút, 1 Thanh và 1 Gối tựa để giải.")
        else:
            with st.spinner("Đang tính toán..."):
                bar_res, react_res = solve_general_truss(
                    st.session_state.nodes,
                    st.session_state.bars,
                    st.session_state.supports,
                    st.session_state.external_forces
                )
                if bar_res is not None:
                    st.session_state.bar_results = bar_res
                    st.session_state.reaction_results = react_res
                    st.success("Đã giải thành công!")
                else:
                    # Lỗi đã được in ra bởi hàm solve_general_truss
                    st.session_state.bar_results = {}
                    st.session_state.reaction_results = {}

    if col2.button("Xóa Toàn Bộ", use_container_width=True):
        # Đã sửa: Xóa sạch mọi thứ
        st.session_state.nodes = {}
        st.session_state.bars = []
        st.session_state.supports = {}
        st.session_state.external_forces = {}
        st.session_state.bar_results = {}
        st.session_state.reaction_results = {}
        st.info("Đã xóa toàn bộ hệ giàn.")
        st.rerun()

    # --- KHU VỰC HIỂN THỊ CHÍNH ---
    
    col_main1, col_main2 = st.columns([0.65, 0.35]) # 65% cho biểu đồ, 35% cho dữ liệu

    with col_main1:
        st.subheader("Biểu đồ Hệ Giàn")
        
        if not st.session_state.nodes:
            st.info("Bắt đầu bằng cách thêm các nút ở thanh bên trái.")
        else:
            fig = plot_truss(
                st.session_state.nodes,
                st.session_state.bars,
                st.session_state.bar_results,
                st.session_state.supports,
                st.session_state.external_forces,
                st.session_state.reaction_results
            )
            st.pyplot(fig)

    with col_main2:
        st.subheader("Dữ liệu Đầu vào")
        with st.expander("Nodes", expanded=True):
            st.json(st.session_state.nodes)
        with st.expander("Bars"):
            st.json(st.session_state.bars)
        with st.expander("Supports"):
            st.json(st.session_state.supports)
        with st.expander("External Forces (Fx, Fy)"):
            st.json(st.session_state.external_forces)
        
        st.subheader("Kết quả Tính toán")
        with st.expander("Nội lực các thanh (S)", expanded=True):
            if not st.session_state.bar_results:
                st.info("Chưa có kết quả.")
            st.json(st.session_state.bar_results)
            
        with st.expander("Phản lực gối tựa (R)", expanded=True):
            if not st.session_state.reaction_results:
                st.info("Chưa có kết quả.")
            st.json(st.session_state.reaction_results)

if __name__ == "__main__":
    main()