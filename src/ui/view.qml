import QtQuick
import QtQuick.Controls
import QtQuick.Shapes

ApplicationWindow {
    id: root
    visible: true
    width: 1920; height: 1080
    color: "black"
    title: "Robot Face Morphing - Clean"

    readonly property color robotBlue: "#00BFFF"

    Item {
        id: face
        width: 1000; height: 700
        anchors.centerIn: parent

        // --- CẤU HÌNH KÍCH THƯỚC ---
        property int eyeWidth: 250
        property int eyeNormalHeight: 250
        property int eyeBlinkHeight: 15
        
        state: "normal" // Đổi thành "happy" để xem mắt cười

        // --- COMPONENT MẮT ---
        component RobotEye : Shape {
            id: eyeShape
            width: face.eyeWidth
            height: face.eyeNormalHeight 

            // Điểm điều khiển độ cong
            property int topCy: 0       // Đỉnh cong trên
            property int bottomCy: height // Đỉnh cong dưới

            // Quan trọng: Bật antialiasing để đường cong mịn màng
            layer.enabled: true
            layer.samples: 4

            ShapePath {
                // Mấu chốt để bo tròn dấu ^ là dùng Stroke (viền) kết hợp Fill (tô)
                strokeColor: root.robotBlue
                fillColor: root.robotBlue
                strokeWidth: 20 // Độ dày của nét vẽ (giúp bo tròn đầu mút)
                
                // Bo tròn các đầu mút
                capStyle: ShapePath.RoundCap 
                joinStyle: ShapePath.RoundJoin

                // Bắt đầu vẽ từ giữa cạnh trái
                startX: 0; startY: eyeShape.height / 2

                // 1. Đường cong trên
                PathQuad {
                    x: eyeShape.width; y: eyeShape.height / 2
                    controlX: eyeShape.width / 2
                    controlY: eyeShape.topCy
                }

                // 2. Đường cong dưới (Vẽ ngược về trái)
                PathQuad {
                    x: 0; y: eyeShape.height / 2
                    controlX: eyeShape.width / 2
                    controlY: eyeShape.bottomCy
                }
            }

            states: [
                State {
                    name: "normal"
                    when: face.state == "normal"
                    // Normal: Top = 0, Bottom = Height => Tạo thành hình bầu dục/tròn đầy đặn
                    PropertyChanges { target: eyeShape; topCy: 0; bottomCy: eyeShape.height }
                },
                State {
                    name: "happy"
                    when: face.state == "happy"
                    // Happy: Bottom ép sát vào Top (cùng thông số) => Diện tích ở giữa = 0
                    // Chỉ còn lại cái viền (Stroke) tạo thành hình cong ^
                    PropertyChanges { target: eyeShape; topCy: -80; bottomCy: -80 }
                }
            ]

            // Animation biến hình dẻo
            transitions: Transition {
                ParallelAnimation {
                    NumberAnimation { property: "topCy"; duration: 350; easing.type: Easing.InOutQuad }
                    NumberAnimation { property: "bottomCy"; duration: 350; easing.type: Easing.InOutQuad }
                }
            }
        }

        // =================== HIỂN THỊ MẮT ===================
        RobotEye {
            id: leftEye
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.horizontalCenter
            anchors.rightMargin: 80
        }

        RobotEye {
            id: rightEye
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.horizontalCenter
            anchors.leftMargin: 80
        }

        // =================== ĐIỀU KHIỂN ===================
        
        // Animation chớp mắt (Chỉ chạy khi Normal)
        SequentialAnimation {
            running: face.state == "normal"
            loops: Animation.Infinite
            
            PauseAnimation { duration: Math.random() * 3000 + 2000 }
            
            // Nhắm
            ParallelAnimation {
                NumberAnimation { target: leftEye; property: "height"; to: face.eyeBlinkHeight; duration: 100 }
                NumberAnimation { target: rightEye; property: "height"; to: face.eyeBlinkHeight; duration: 100 }
            }
            
            PauseAnimation { duration: 50 }
            
            // Mở
            ParallelAnimation {
                NumberAnimation { target: leftEye; property: "height"; to: face.eyeNormalHeight; duration: 150; easing.type: Easing.OutBack }
                NumberAnimation { target: rightEye; property: "height"; to: face.eyeNormalHeight; duration: 150; easing.type: Easing.OutBack }
            }
        }

        // Timer tự động đổi biểu cảm (Demo)
        Timer {
            interval: 3000; running: true; repeat: true
            onTriggered: {
                face.state = (face.state === "normal" ? "happy" : "normal")
            }
        }
        
        // Click chuột để đổi ngay lập tức
        MouseArea {
            anchors.fill: parent
            onClicked: face.state = (face.state === "normal" ? "happy" : "normal")
        }
    }
}