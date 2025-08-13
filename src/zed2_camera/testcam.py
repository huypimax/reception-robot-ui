import os
import cv2
import numpy as np
import pyzed.sl as sl


def run_zed_depth_estimation():
    # 1. Tạo một đối tượng Camera ZED
    zed = sl.Camera()

    # 2. Đặt tham số cấu hình camera
    init_params = sl.InitParameters()
    init_params.camera_resolution = (
        sl.RESOLUTION.HD720
    )  # Chọn độ phân giải (HD1080, HD720, VGA)
    init_params.depth_mode = (
        sl.DEPTH_MODE.ULTRA
    )  # Chọn chế độ sâu (NEURAL, ULTRA, QUALITY, PERFORMANCE)
    init_params.coordinate_units = (
        sl.UNIT.METER
    )  # Đơn vị cho độ sâu (METER, MILLIMETER, CENTIMETER, INCH, FOOT)
    init_params.camera_fps = 30  # FPS mong muốn

    # 3. Mở camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Cannot open camera: {err}")
        exit(1)

    print("ZED Camera đã được mở thành công. Nhấn 'q' để thoát.")

    # Tạo các đối tượng chứa dữ liệu hình ảnh và độ sâu
    image_zed = sl.Mat()  # Chứa ảnh RGB/BGR
    depth_zed = sl.Mat()  # Chứa bản đồ độ sâu
    point_cloud_zed = sl.Mat()  # Chứa đám mây điểm (nếu cần)

    # Biến để lưu trữ trạng thái runtime
    runtime_parameters = sl.RuntimeParameters()
    # Chế độ lọc độ sâu (có thể là sl.REFERENCE_FRAME.WORLD hoặc sl.REFERENCE_FRAME.CAMERA)
    # runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD

    # Lấy thông tin camera để tính toán trực quan
    camera_information = zed.get_camera_information()
    # f_x = camera_information.calibration_parameters.left_cam.fx
    # f_y = camera_information.calibration_parameters.left_cam.fy
    # baseline = camera_information.calibration_parameters.T[0] # Khoảng cách giữa 2 camera

    while True:
        # Lấy khung hình mới từ camera
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # 4. Lấy ảnh (ví dụ: ảnh bên trái)
            zed.retrieve_image(image_zed, sl.VIEW.LEFT)
            # 5. Lấy bản đồ độ sâu
            zed.retrieve_measure(depth_zed, sl.MEASURE.DEPTH)
            # 6. Lấy đám mây điểm (tùy chọn)
            # zed.retrieve_measure(point_cloud_zed, sl.MEASURE.XYZRGBA)

            # Chuyển đổi dữ liệu ZED thành định dạng OpenCV (NumPy array)
            # Ảnh
            img_np = image_zed.get_data()
            img_cv = cv2.cvtColor(
                img_np, cv2.COLOR_RGBA2BGR
            )  # ZED trả về RGBA, cần chuyển sang BGR cho OpenCV

            # Bản đồ độ sâu
            depth_np = depth_zed.get_data()  # Giá trị độ sâu thực (float32)

            # --- Hiển thị ảnh và bản đồ độ sâu ---
            # Hiển thị ảnh màu từ camera ZED
            cv2.imshow("ZED Camera Left Image", img_cv)
# Để hiển thị bản đồ độ sâu, chúng ta cần chuẩn hóa nó để có thể nhìn thấy bằng mắt thường
# Các giá trị độ sâu thường từ 0 đến vài mét.
# Chúng ta sẽ chuẩn hóa để hiển thị từ 0-255.
            # Lưu ý: NaN (Not a Number) trong bản đồ độ sâu là các điểm không xác định được độ sâu.
            depth_display = np.copy(depth_np)
            depth_display[np.isnan(depth_display)] = (
                0  # Gán 0 cho NaN để không làm hỏng chuẩn hóa
            )

            # Chỉ chuẩn hóa các giá trị lớn hơn 0 để tránh ảnh hưởng bởi các điểm 0 hoặc NaN
            # Tìm min/max của các giá trị độ sâu hợp lệ (ví dụ: > 0 và < 20 mét)
            min_depth_val = 0.5  # Khoảng cách tối thiểu có ý nghĩa
            max_depth_val = 5.0  # Khoảng cách tối đa muốn hiển thị (có thể điều chỉnh)

            # Tạo một mask cho các giá trị hợp lệ
            valid_mask = (depth_display > min_depth_val) & (
                depth_display < max_depth_val
            )

            if np.any(valid_mask):
                # Chuẩn hóa chỉ trên các giá trị hợp lệ
                normalized_depth = (depth_display[valid_mask] - min_depth_val) / (
                    max_depth_val - min_depth_val
                )
                normalized_depth = np.clip(
                    normalized_depth, 0, 1
                )  # Giới hạn trong khoảng 0-1

                depth_output = np.zeros_like(depth_display, dtype=np.uint8)
                depth_output[valid_mask] = (normalized_depth * 255).astype(np.uint8)
            else:
                depth_output = np.zeros_like(
                    depth_display, dtype=np.uint8
                )  # Tất cả màu đen nếu không có giá trị hợp lệ

            # Áp dụng colormap để dễ nhìn hơn
            depth_colormap = cv2.applyColorMap(depth_output, cv2.COLORMAP_JET)
            cv2.imshow("ZED Depth Map", depth_colormap)

            # --- Ví dụ lấy độ sâu của một điểm cụ thể (ví dụ: tâm ảnh) ---
            # center_x, center_y = img_cv.shape[1] // 2, img_cv.shape[0] // 2
            # depth_at_center = depth_np[center_y, center_x]
            # if not np.isnan(depth_at_center):
            #     print(f"Độ sâu tại tâm ảnh: {depth_at_center:.2f} {init_params.coordinate_units.name}")

            # Thoát nếu nhấn 'q'
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

    # Đóng camera
    zed.close()
    cv2.destroyAllWindows()
    print("ZED Camera  closed.")


if __name__ == "__main__":
    run_zed_depth_estimation()