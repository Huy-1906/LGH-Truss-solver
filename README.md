# Chương trình Phân tích tính toán Hệ Giàn Phẳng 2D

## Giới thiệu
Đây là ứng dụng web tương tác được phát triển bằng Python và Streamlit để phân tích các hệ giàn phẳng 2D. Chương trình cho phép người dùng xây dựng, phân tích và tính toán ứng lực trong các thanh của hệ giàn một cách trực quan và dễ dàng.

## Tính năng chính
1. **Giao diện tương tác:**
   - Thêm/xóa nút (nodes) với tọa độ (x,y)
   - Thêm/xóa thanh (bars) kết nối giữa các nút
   - Đặt gối tựa (pin hoặc roller) tại các nút
   - Thêm ngoại lực tác dụng lên các nút
   - Hiển thị trực quan hệ giàn

2. **Tính toán:**
   - Sử dụng phương pháp ma trận để giải hệ giàn
   - Tính toán ứng lực trong các thanh
   - Xác định phản lực tại các gối tựa
   - Kiểm tra tính ổn định của hệ

3. **Hiển thị kết quả:**
   - Biểu đồ hệ giàn với các thanh và nút
   - Hiển thị giá trị ứng lực trong từng thanh
   - Hiển thị phản lực tại các gối
   - Phân biệt thanh chịu kéo/nén bằng màu sắc

## Cấu trúc thư mục
```
LGH/
│
├── main.py               # File chính chứa giao diện người dùng
│
└── function/            # Thư mục chứa các module chức năng
    ├── solve_general_truss.py      # Module giải hệ giàn
    ├── calculate_bar_properties.py  # Tính toán đặc trưng của thanh
    └── plot_truss.py               # Module vẽ hệ giàn
```

## Yêu cầu hệ thống
- Python 3.7 trở lên
- Các thư viện Python:
  - streamlit
  - numpy
  - matplotlib
  - pandas (nếu cần xuất dữ liệu)

## Hướng dẫn cài đặt
1. Clone repository hoặc tải về máy
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install streamlit numpy matplotlib
   ```
3. Chạy chương trình:
   ```bash
   streamlit run main.py
   ```

## Cách sử dụng
1. **Thêm nút (Nodes):**
   - Nhập tên nút (ví dụ: A, B, C...)
   - Nhập tọa độ x, y
   - Nhấn "Thêm Nút"

2. **Thêm thanh (Bars):**
   - Chọn hai nút để kết nối
   - Nhấn "Thêm Thanh"

3. **Đặt gối tựa (Supports):**
   - Chọn nút cần đặt gối
   - Chọn loại gối (pin hoặc roller)
   - Nhấn "Đặt/Cập nhật Gối tựa"

4. **Thêm lực tác dụng:**
   - Chọn nút chịu lực
   - Nhập giá trị lực theo phương x và y
   - Nhấn "Thêm/Cập nhật Lực"

5. **Phân tích hệ:**
   - Nhấn "Giải Hệ Giàn" để tính toán
   - Xem kết quả ứng lực và phản lực

## Lưu ý quan trọng
- Đảm bảo hệ giàn ổn định trước khi tính toán
- Kiểm tra các điều kiện biên và lực tác dụng
- Chú ý đến đơn vị của lực và khoảng cách

## Xử lý lỗi thường gặp
1. **Hệ không ổn định:**
   - Kiểm tra số lượng và vị trí gối tựa
   - Đảm bảo kết cấu hệ giàn hợp lý

2. **Ma trận suy biến:**
   - Kiểm tra vị trí các thanh
   - Đảm bảo không có thanh trùng nhau

## Tác giả
- 2452391 - Lý Gia Huy

## Giấy phép
Dự án này được phát triển cho mục đích học tập và nghiên cứu.

## Liên hệ
Nếu có bất kỳ câu hỏi hoặc góp ý, vui lòng liên hệ qua email hoặc tạo issue trên repository.# LGH-Truss-solver
