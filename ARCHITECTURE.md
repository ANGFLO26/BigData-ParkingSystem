# 🏗️ Kiến trúc Hệ thống Đỗ Xe Phân tán

## 📊 Overview

Hệ thống đỗ xe được thiết kế theo kiến trúc phân tán với 6 nodes, mỗi node đảm nhiệm một chức năng cụ thể.

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    NODE 2: Camera Producer                  │
│  - Mô phỏng camera AI                                       │
│  - Tạo parking events (ENTERING, PARKED, MOVING, EXITING)  │
│  - Gửi events lên Kafka topic: parking-events              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │ Kafka Stream
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              NODE 3: Spark Structured Streaming            │
│  - Đọc events từ Kafka                                      │
│  - Stateful processing: Track parking duration              │
│  - Tính tiền: 1 phút = 10,000 VNĐ                          │
│  - Cập nhật state realtime                                 │
└──────────┬───────────────────────────────────┬─────────────┘
           │                                   │
           │                                   │
    ┌──────▼──────┐                    ┌─────▼──────┐
    │  Node 5:    │                    │  Node 4:   │
    │   Redis     │                    │ Cassandra  │
    │ (Realtime)  │                    │ (History)  │
    └─────────────┘                    └────────────┘
           │                                   │
           │                                   │
           └───────────┬───────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │  Node 6: Dashboard    │
           │  (Streamlit GUI)      │
           │  - Đọc từ Redis       │
           │  - Hiển thị realtime  │
           └───────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    NODE 1: Airflow                           │
│  - Điều phối và giám sát toàn hệ thống                      │
│  - Health checks cho tất cả nodes                           │
│  - Tạo báo cáo định kỳ                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ Component Details

### Node 1: Airflow + Redis (Celery)
- **Airflow**: Workflow orchestration
- **Redis (Celery)**: Task queue broker
- **PostgreSQL**: Airflow metadata database
- **Chức năng**: 
  - Monitor health của các nodes
  - Schedule jobs định kỳ
  - Generate reports

### Node 2: Camera Producer + Kafka
- **Kafka Broker**: Message broker
- **Zookeeper**: Kafka coordination
- **Camera Producer**: Python script mô phỏng camera AI
- **Chức năng**:
  - Tạo parking events
  - Gửi lên Kafka topic `parking-events`
  - Rate: ~1 event/3 giây

### Node 3: Spark Streaming
- **Apache Spark**: Distributed processing
- **Structured Streaming**: Real-time processing
- **Chức năng**:
  - Đọc từ Kafka
  - Track state mỗi xe (license_plate, location, start_time)
  - Tính tiền realtime: `fee = duration_minutes * 10000`
  - Ghi vào Redis (realtime) và Cassandra (history)

### Node 4: Cassandra
- **Apache Cassandra**: NoSQL database
- **Keyspace**: `parking_system`
- **Table**: `parking_history`
- **Chức năng**:
  - Lưu lịch sử đỗ xe
  - Query theo license_plate hoặc location
  - Persistence dài hạn

### Node 5: Redis Cache
- **Redis**: In-memory cache
- **Database**: 2 (tách biệt với Redis Celery)
- **Data structure**: Key-value
- **Keys**:
  - `parking:total_locations`: Tổng số vị trí
  - `parking:occupied_count`: Số vị trí có xe
  - `parking:empty_count`: Số vị trí trống
  - `parking:location:{A1}`: Chi tiết từng vị trí (JSON)
- **TTL**: 3600 giây (1 giờ)

### Node 6: Streamlit Dashboard
- **Streamlit**: Python web framework
- **Chức năng**:
  - Đọc từ Redis (realtime)
  - Hiển thị bản đồ bãi đỗ
  - Hiển thị thông tin từng xe (biển số, thời gian, phí)
  - Auto-refresh mỗi 2 giây
  - Tổng doanh thu

## 💾 Data Models

### Parking Event (Kafka)
```json
{
  "timestamp": "2024-01-01 10:00:00",
  "timestamp_unix": 1704096000,
  "license_plate": "29A-12345",
  "location": "A1",
  "status_code": "PARKED"
}
```

### Location Data (Redis)
```json
{
  "license_plate": "29A-12345",
  "status": "occupied",
  "parking_duration_minutes": 15.5,
  "parking_fee": 155000,
  "start_time": 1704096000
}
```

### Parking History (Cassandra)
```cql
CREATE TABLE parking_history (
    timestamp TIMESTAMP,
    license_plate TEXT,
    location TEXT,
    status_code TEXT,
    parking_duration_minutes DECIMAL,
    parking_fee DECIMAL,
    PRIMARY KEY ((license_plate), timestamp)
);
```

## 🔢 Tính tiền đỗ xe

### Công thức:
```
duration_seconds = current_time - parked_start_time
duration_minutes = duration_seconds / 60.0
parking_fee = duration_minutes * 10000 (VNĐ)
```

### Ví dụ:
- Đỗ 15 phút 30 giây = 15.5 phút = **155,000 VNĐ**
- Đỗ 1 giờ = 60 phút = **600,000 VNĐ**
- Đỗ 2 giờ 15 phút = 135 phút = **1,350,000 VNĐ**

## 🔄 State Management

### Spark Stateful Processing:
1. **Track state per vehicle:**
   - `vehicle_state[license_plate] = {location, start_time_unix, status}`

2. **Status transitions:**
   - `ENTERING` → `PARKED` (lưu start_time)
   - `PARKED` → Tính tiền realtime
   - `PARKED` → `MOVING` → `EXITING` (tính tiền cuối cùng, clear state)

3. **Watermarking:**
   - Window: 10 phút
   - Trigger: Mỗi 10 giây

## 🌐 Network Configuration

### Ports:
- **Kafka**: 9092 (external), 9093 (internal)
- **Zookeeper**: 2181
- **Redis**: 6379
- **Cassandra**: 9042 (CQL), 7000 (inter-node)
- **Spark**: 7077 (master), 8080 (UI), 4040 (app UI)
- **Airflow**: 8080
- **Dashboard**: 8501

### IP Configuration:
- Mỗi node có IP riêng (ví dụ: 192.168.1.10-15)
- Cấu hình trong `.env` file
- Docker network: `parking-network` (bridge)

## 📈 Scalability

### Hiện tại:
- Single broker Kafka
- Single node Cassandra
- Single Spark master
- Single Redis instance

### Có thể scale:
- Kafka: Thêm brokers
- Spark: Thêm workers
- Cassandra: Cluster mode
- Redis: Sentinel hoặc Cluster mode

## 🔐 Security (Tương lai)

- Authentication cho Kafka
- SSL/TLS encryption
- Redis password
- Cassandra authentication
- Dashboard authentication

