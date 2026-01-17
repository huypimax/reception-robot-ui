import QtQuick
import QtQuick.Controls
import QtQuick.Shapes

ApplicationWindow {
    id: root 
    visible: true
    width: 1920 // Kích thước màn hình 
    height: 1080
    title: "Robot Face Animation"
    color: "black" // Nền đen 

    // --- KHU VỰC CẤU HÌNH (Sửa thông số ở đây) ---
    readonly property color robotBlue: "#00BFFF"
    
    // --- CONTAINER CHÍNH (Nhóm các bộ phận lại để dễ căn giữa) ---
    Item {
        id: face
        width: 1000; height: 700
        anchors.centerIn: parent

        // Chiều cao mắt
        property int eyeWidth: 250      // Chiều rộng mắt
        property int eyeNormalHeight: 250 // Chiều cao lúc mở (Sửa ở đây là ăn hết)
        property int eyeBlinkHeight: 15   // Chiều cao lúc nhắm

        // =================== CON MẮT TRÁI ===================
        Rectangle {
            id: leftEye
            width: face.eyeWidth
            height: face.eyeNormalHeight     
            radius: width / 2 // Bo tròn 50% để tạo hình tròn
            color: robotBlue // Màu nền của mắt (vòng ngoài)
            
            // Căn vị trí: nằm giữa theo chiều dọc, lệch sang trái so với tâm
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.horizontalCenter
            anchors.rightMargin: 100 // Khoảng cách giữa 2 mắt
            

            // --- Đồng tử (Tròng mắt bên trong) ---
            Rectangle {
                width: parent.width * 0.6  // Kích thước nhỏ hơn mắt chính
                height: parent.height * 0.6
                radius: width / 2
                color: "#0077be" // Màu xanh đậm hơn một chút để tạo chiều sâu
                anchors.centerIn: parent // Căn giữa con mắt
                // Dịch chuyển lên trên một xíu để trông dễ thương hơn
                anchors.verticalCenterOffset: -parent.height * 0.1
            }
        }

        // =================== CON MẮT PHẢI ===================
        Rectangle {
            id: rightEye
            width: face.eyeWidth
            height: face.eyeNormalHeight
            radius: width / 2
            color: robotBlue
            
            // Căn vị trí: nằm giữa theo chiều dọc, lệch sang phải so với tâm
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.horizontalCenter
            anchors.leftMargin: 100

            // Đồng tử
            Rectangle {
                width: parent.width * 0.6
                height: parent.height * 0.6
                radius: width / 2
                color: "#0077be"
                anchors.centerIn: parent
                anchors.verticalCenterOffset: -parent.height * 0.1
            }
        }
        
        // =================== HIỆU ỨNG CHỚP MẮT ĐỒNG BỘ ===================
        // Dùng một SequentialAnimation chung để điều khiển cả 2 mắt cùng lúc
        SequentialAnimation {
            running: true // Tự động chạy ngay khi load
            loops: Animation.Infinite // Lặp lại mãi mãi

            // 1. Thời gian mở mắt bình thường (ngẫu nhiên từ 2 đến 5 giây)
            PauseAnimation { duration: Math.random() * 3000 + 2000}

            // 2. Nhắm lại nhanh (Giảm chiều cao cả 2 mắt xuống còn 15px)
            ParallelAnimation {
                NumberAnimation { target: leftEye; property: "height"; to: face.eyeBlinkHeight; duration: 100; easing.type: Easing.InQuad }
                NumberAnimation { target: rightEye; property: "height"; to: face.eyeBlinkHeight; duration: 100; easing.type: Easing.InQuad }
            }
            
            // 3. Giữ trạng thái nhắm trong tích tắc
            PauseAnimation { duration: 50 }

            // 4. Mở ra nhanh (Trở lại chiều cao gốc 180px)
            // Sử dụng Easing.OutBack để tạo hiệu ứng bật nảy nhẹ khi mở mắt
            ParallelAnimation {
                NumberAnimation { target: leftEye; property: "height"; to: face.eyeNormalHeight; duration: 150; easing.type: Easing.OutBack }
                NumberAnimation { target: rightEye; property: "height"; to: face.eyeNormalHeight; duration: 150; easing.type: Easing.OutBack }
            }
        }

        // =================== CÁI MIỆNG CƯỜI ===================
        Shape {
            // Đặt vị trí miệng nằm dưới 2 mắt
            anchors.top: leftEye.bottom
            anchors.topMargin: 40
            anchors.horizontalCenter: parent.horizontalCenter
            
            width: 70 // Độ rộng tổng thể của miệng
            height: 20  // Độ sâu của nụ cười

            // Đối tượng vẽ nét
            ShapePath {
                strokeColor: robotBlue // Màu nét vẽ
                strokeWidth: 12        // Độ dày của nét
                fillColor: "transparent" // Không tô màu nền bên trong
                capStyle: ShapePath.RoundCap // Bo tròn 2 đầu mút của nét vẽ cho mềm mại

                // Bắt đầu vẽ từ điểm trên cùng bên trái (0,0)
                startX: 0; startY: 0
                
                // Vẽ một đường cong Quad (Quadratic Bezier)
                PathQuad {
                    x: 70; y: 0         // Điểm kết thúc ở trên cùng bên phải
                    // Điểm điều khiển nằm ở giữa và thấp xuống dưới để tạo độ cong
                    controlX: 35; controlY: 50 
                }
            }
        }
    }
}