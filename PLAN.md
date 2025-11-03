# 🚀 KẾ HOẠCH TRIỂN KHAI HỆ THỐNG ĐỖ XE PHÂN TÁN

## 📋 TỔNG QUAN KIẾN TRÚC

### 🟦 Node 1: Airflow + Redis (Celery)
- **Mục đích**: Trung tâm điều phối & giám sát toàn hệ thống
- **Component**: Apache Airflow, Redis (Celery broker)
- **Kết nối**: Tất cả các node

### 🟩 Node 2: Camera Producer + Kafka Broker
- **Mục đích**: Mô phỏng camera AI gửi dữ liệu vào luồng
- **Component**: Python Kafka Producer, Apache Kafka
- **Kết nối**: Spark Streaming (Node 3)

### 🟨 Node 3: Spark Streaming Processor
- **Mục đích**: Nhận data từ Kafka, xử lý logic & tính tiền
- **Component**: Apache Spark Structured Streaming (Stateful)
- **Kết nối**: Redis (Node 5), Cassandra (Node 4)

### 🟧 Node 4: Cassandra Database
- **Mục đích**: Lưu trữ dữ liệu dài hạn (lịch sử đỗ xe, phí, thời gian)
- **Component**: Apache Cassandra
- **Kết nối**: Spark (ghi), Dashboard (đọc bổ sung)

### 🟥 Node 5: Redis (Realtime Cache)
- **Mục đích**: Lưu dữ liệu tạm thời để hiển thị nhanh
- **Component**: Redis (Database 2)
- **Kết nối**: Spark (ghi), Dashboard (đọc)

### 🟪 Node 6: Realtime Dashboard (GUI)
- **Mục đích**: Hiển thị trạng thái bãi đỗ, xe, phí realtime
- **Component**: Flask / Streamlit + Redis client
- **Kết nối**: Redis (Node 5), Cassandra (Node 4), Airflow (trigger)

---

## 🔧 CÁC BƯỚC THỰC HIỆN

### BƯỚC 1: Tạo Docker Network & Compose Infrastructure
**Mục tiêu**: Setup môi trường Docker để chạy phân tán

**Công việc**:
1. Tạo `docker-compose.yml` với 6 services tương ứng 6 nodes
2. Tạo Docker network để các container giao tiếp
3. Tạo Dockerfile cho mỗi component (nếu cần)
4. Setup volumes và persistent storage
5. Cấu hình environment variables

**Output**: 
- `docker-compose.yml`
- `Dockerfile.*` (nếu cần)
- `.env` file
- Network configuration

---

### BƯỚC 2: Node 2 - Camera Producer + Kafka
**Mục tiêu**: Convert code hiện tại thành Kafka Producer

**Công việc**:
1. Tạo `producer/camera_producer.py` từ `parking_json_stream.py`
2. Tích hợp Kafka Producer client
3. Gửi events lên Kafka topic `parking-events`
4. Cấu hình Kafka broker trong Docker
5. Test producer gửi data thành công

**Output**:
- `producer/camera_producer.py`
- Kafka configuration trong docker-compose
- Kafka topic setup script

---

### BƯỚC 3: Node 3 - Spark Structured Streaming (Stateful)
**Mục tiêu**: Xử lý realtime, tính tiền theo block 10 phút

**Công việc**:
1. Tạo `spark/spark_streaming.py` với Structured Streaming
2. **Logic tính tiền theo block 10 phút**:
   - Nhận event từ Kafka
   - Track state của mỗi xe (location, start_time, license_plate)
   - Tính số block 10 phút đã đỗ
   - Tính tiền = số_block * đơn_giá_block
   - Cập nhật state khi xe EXITING
3. **Stateful Processing**:
   - Sử dụng `groupBy` + `agg` với window functions
   - Track parking duration per vehicle
   - Calculate parking fee
4. Ghi kết quả vào Redis (Node 5) và Cassandra (Node 4)

**Output**:
- `spark/spark_streaming.py`
- Spark configuration
- State management logic

**Công thức tính tiền**:
```
parking_duration_seconds = current_time - parked_start_time
parking_duration_minutes = parking_duration_seconds / 60
number_of_blocks = ceil(parking_duration_minutes / 10)
parking_fee = number_of_blocks * price_per_block
```

---

### BƯỚC 4: Node 4 & 5 - Cassandra & Redis Setup
**Mục tiêu**: Setup databases để lưu trữ và cache

**Node 4 - Cassandra**:
1. Tạo keyspace và tables
2. Schema cho lịch sử đỗ xe
3. Spark write connector

**Node 5 - Redis**:
1. Setup Redis với database 2
2. Cấu hình TTL cho cache
3. Spark write connector cho realtime data
4. Data format: `parking:location:{location_id}` -> JSON

**Output**:
- Cassandra schema (`cassandra/schema.cql`)
- Redis configuration
- Spark connectors

---

### BƯỚC 5: Node 6 - Realtime Dashboard (GUI)
**Mục tiêu**: Tạo GUI hiển thị trạng thái realtime

**Công việc**:
1. Chọn framework (Flask hoặc Streamlit)
2. Tạo dashboard với:
   - **Bảng tổng quan**: Tổng số vị trí có xe / trống
   - **Chi tiết từng vị trí**: Location, biển số, thời gian đỗ, phí
   - **Auto-refresh** từ Redis
   - **Lịch sử** từ Cassandra (optional)
3. API endpoints hoặc Streamlit components
4. Real-time updates với WebSocket hoặc polling

**Output**:
- `dashboard/app.py` (Flask hoặc Streamlit)
- `dashboard/templates/` (nếu Flask)
- Static files (CSS, JS)

---

### BƯỚC 6: Node 1 - Airflow Orchestration
**Mục tiêu**: Điều phối và giám sát toàn hệ thống

**Công việc**:
1. Tạo Airflow DAG để:
   - Trigger Spark job
   - Monitor Kafka topics
   - Health check các services
   - Backup data (optional)
2. Setup Airflow connections
3. Tạo monitoring dashboard

**Output**:
- `airflow/dags/parking_system_dag.py`
- Airflow configuration

---

### BƯỚC 7: Testing & Documentation
**Mục tiêu**: Đảm bảo hệ thống hoạt động đúng

**Công việc**:
1. Test end-to-end flow
2. Test tính tiền đúng theo block 10 phút
3. Test realtime updates
4. Tạo documentation:
   - README.md với hướng dẫn setup
   - Architecture diagram
   - API documentation
   - Demo script

**Output**:
- `README.md`
- `docs/ARCHITECTURE.md`
- Test results
- Demo script

---

## 📦 CẤU TRÚC THƯ MỤC DỰ KIẾN

```
bigdata/
├── docker-compose.yml          # Main orchestration file
├── .env                        # Environment variables
├── README.md                   # Documentation
│
├── producer/                   # Node 2
│   ├── Dockerfile
│   ├── camera_producer.py      # Kafka Producer
│   └── requirements.txt
│
├── spark/                      # Node 3
│   ├── Dockerfile
│   ├── spark_streaming.py      # Spark Structured Streaming
│   ├── requirements.txt
│   └── spark-submit.sh
│
├── cassandra/                  # Node 4
│   ├── Dockerfile
│   ├── schema.cql              # Database schema
│   └── init-scripts/
│
├── redis/                      # Node 5
│   ├── redis.conf
│   └── Dockerfile
│
├── dashboard/                  # Node 6
│   ├── Dockerfile
│   ├── app.py                  # Flask/Streamlit app
│   ├── requirements.txt
│   └── templates/              # (nếu Flask)
│
├── airflow/                    # Node 1
│   ├── Dockerfile
│   ├── dags/
│   │   └── parking_system_dag.py
│   ├── config/
│   └── requirements.txt
│
└── kafka/                      # Node 2
    ├── kafka-setup.sh
    └── server.properties
```

---

## 🔑 CÁC ĐIỂM QUAN TRỌNG CẦN LƯU Ý

### 1. Tính tiền theo block 10 phút
- **Logic**: Mỗi block = 10 phút, làm tròn lên
- **Ví dụ**: Đỗ 15 phút = 2 blocks, đỗ 25 phút = 3 blocks
- **Đơn giá**: Có thể config trong environment variable

### 2. Spark Stateful Processing
- Sử dụng **Watermark** để xử lý late events
- **Window functions** để nhóm events theo thời gian
- **State store** để track parking duration của mỗi xe

### 3. Realtime Updates
- Redis cache được update mỗi khi có event mới
- Dashboard polling Redis mỗi 1-2 giây
- Hoặc dùng WebSocket cho real-time hơn

### 4. Distributed Setup
- Mỗi node chạy trong container riêng
- Có thể scale Spark workers bằng docker-compose scale
- Network isolation nhưng vẫn giao tiếp được

---

## ⏱️ THỨ TỰ THỰC HIỆN

1. **Bước 1**: Setup Docker infrastructure (30 phút)
2. **Bước 2**: Kafka Producer (30 phút)
3. **Bước 3**: Spark Streaming (60 phút) - **QUAN TRỌNG NHẤT**
4. **Bước 4**: Databases setup (30 phút)
5. **Bước 5**: Dashboard (45 phút)
6. **Bước 6**: Airflow (30 phút)
7. **Bước 7**: Testing & Docs (30 phút)

**Tổng thời gian ước tính**: 4-5 giờ

---

## ✅ CHECKLIST TRƯỚC KHI BẮT ĐẦU CODE

- [x] Đã đọc và hiểu code hiện tại
- [x] Đã phân tích kiến trúc 6 nodes
- [x] Đã lên kế hoạch chi tiết
- [ ] Cần xác nhận: Đơn giá mỗi block 10 phút là bao nhiêu? (có thể để default)
- [ ] Cần xác nhận: Framework cho Dashboard? (Flask hay Streamlit - recommend Streamlit cho nhanh)

