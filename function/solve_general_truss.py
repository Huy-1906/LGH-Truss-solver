def solve_general_truss(nodes, bars, supports, external_forces):
    """
    Giải hệ giàn 2D tổng quát.
    """
    
    node_names = list(nodes.keys())
    num_nodes = len(node_names)
    num_bars = len(bars)
    
    # 1. Xác định số bậc tự do (DOF) và các phản lực
    reactions = [] # Danh sách các phản lực [('Tên nút', 'hướng'), ...]
    dof_map = {} # Ánh xạ (tên nút, hướng) -> số thứ tự của bậc tự do
    
    for i, name in enumerate(node_names):
        support_type = supports.get(name)
        
        # X-DOF
        if support_type == 'pin' or support_type == 'roller_x':
            reactions.append((name, 'x'))
            dof_map[(name, 'x')] = -1 # -1 nghĩa là bị chặn (có phản lực)
        else:
            dof_map[(name, 'x')] = i * 2
            
        # Y-DOF
        if support_type == 'pin' or support_type == 'roller_y':
            reactions.append((name, 'y'))
            dof_map[(name, 'y')] = -1
        else:
            dof_map[(name, 'y')] = i * 2 + 1
            
    num_reactions = len(reactions)
    num_unknowns = num_bars + num_reactions
    
    # 2. Xây dựng ma trận A
    num_eq = 2 * num_nodes
    A = np.zeros((num_eq, num_unknowns))
    F_ext = np.zeros(num_eq)
    
    # Lặp qua từng nút để xây dựng các hàng của ma trận A
    for i, node_name in enumerate(node_names):
        eq_x = 2 * i     # Hàng cho phương trình Fx = 0
        eq_y = 2 * i + 1   # Hàng cho phương trình Fy = 0
        
        # 2a. Thêm ngoại lực (External Forces) vào véc-tơ F
        force = external_forces.get(node_name, [0, 0])
        F_ext[eq_x] = force[0]
        F_ext[eq_y] = force[1]
        
        # 2b. Thêm nội lực (Bar Forces) vào ma trận A
        for j, bar_nodes in enumerate(bars):
            # Sắp xếp để đảm bảo tên thanh nhất quán (A,B) thay vì (B,A)
            n1, n2 = tuple(sorted(bar_nodes))
            
            if n1 == node_name:
                n_start, n_end = nodes[n1], nodes[n2]
            elif n2 == node_name:
                n_start, n_end = nodes[n2], nodes[n1]
            else:
                continue
                
            _, c, s = calculate_bar_properties(n_start, n_end)
            A[eq_x, j] = c # Thành phần Fx
            A[eq_y, j] = s # Thành phần Fy

        # 2c. Thêm phản lực (Reactions) vào ma trận A
        for k, (r_node, r_dir) in enumerate(reactions):
            if r_node == node_name:
                unknown_index = num_bars + k
                if r_dir == 'x':
                    A[eq_x, unknown_index] = 1
                elif r_dir == 'y':
                    A[eq_y, unknown_index] = 1

    # 3. Giải hệ phương trình A * X = -F_ext
    try:
        if num_eq != num_unknowns:
            st.error(f"Hệ không ổn định (hoặc siêu tĩnh)! "
                     f"Số phương trình ({num_eq}) khác số ẩn ({num_unknowns}).")
            st.error(f"Số ẩn = {num_bars} thanh + {num_reactions} phản lực = {num_unknowns}")
            return None, None
            
        X = np.linalg.solve(A, -F_ext)
        
        bar_forces = X[:num_bars]
        reaction_forces = X[num_bars:]
        
        # Đóng gói kết quả với tên thanh đã sắp xếp
        bar_results = {f"S_{sorted(bars[i])[0]}-{sorted(bars[i])[1]}": force for i, force in enumerate(bar_forces)}
        reaction_results = {f"R_{reactions[i][0]}_{reactions[i][1]}": force for i, force in enumerate(reaction_forces)}
        
        return bar_results, reaction_results
        
    except np.linalg.LinAlgError:
        st.error("Lỗi: Hệ không xác định hoặc ma trận suy biến. "
                 "Hãy kiểm tra lại gối tựa và kết cấu của hệ giàn.")
        return None, None
