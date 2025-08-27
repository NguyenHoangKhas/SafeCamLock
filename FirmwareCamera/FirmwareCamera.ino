#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// ===========================
// WiFi
// ===========================
const char* ssid = "Trai Nguyen";
const char* password = "12345678";
String serverUrl = "http://192.168.1.12:8000/recognize";

// ===========================
// Relay (điều khiển khóa điện từ)
// ===========================
int relayPin = 12;   // IO12 trên ESP32-CAM

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  // Relay setup
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);   // ban đầu tắt (relay thường LOW = OFF)

  // ===========================
  // Camera config
  // ===========================
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count = 2;
  }

  // Khởi tạo camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed 0x%x\n", err);
    return;
  }

  // WiFi
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);

    if (httpResponseCode > 0) {
      Serial.printf("HTTP Response code: %d\n", httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);

      // 🔑 Nếu server nhận diện thành công → mở khóa
      // 🔑 Nếu server nhận diện thành công → mở khóa
    if (payload.indexOf("Đã lưu face login") >= 0) {   // server trả về thông báo login thành công
        Serial.println("✅ Nhận diện thành công → Mở khóa!");
        digitalWrite(relayPin, HIGH);     // bật relay
        delay(3000);                      // mở 3 giây
        digitalWrite(relayPin, LOW);      // tắt relay
    }


    } else {
      Serial.printf("Error code: %d\n", httpResponseCode);
    }

    http.end();
    esp_camera_fb_return(fb);

    delay(2000);  // chụp & gửi ảnh mỗi 2 giây
  }
}
