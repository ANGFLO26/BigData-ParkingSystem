# 🚗 Hệ Thống Đỗ Xe Thông Minh - Distributed Big Data System

Hệ thống tính tiền đỗ xe theo thời gian thực sử dụng Kafka, Spark Structured Streaming, Redis, Cassandra và Streamlit Dashboard.

## 📋 Tổng quan

Hệ thống được thiết kế để chạy phân tán trên 6 máy Ubuntu, mỗi máy đảm nhiệm một chức năng riêng:

- **Node 1**: Airflow + Redis (Celery) - Điều phối & giám sát
- **Node 2**: Camera Producer + Kafka Broker - Mô phỏng camera AI
- **Node 3**: Spark Streaming Processor - Xử lý realtime & tính tiền
- **Node 4**: Cassandra Database - Lưu trữ lịch sử
- **Node 5**: Redis Cache - Cache realtime
- **Node 6**: Streamlit Dashboard - GUI hiển thị trạng thái

## 🔧 Cài đặt

### Yêu cầu

- Docker và Docker Compose trên mỗi máy
- Python 3.9+ (nếu chạy không dùng Docker)
- Tất cả các máy trong cùng mạng LAN

### Bước 1: Clone project

Trên máy master, clone repository:
```bash
git clone <repository-url>
cd bigdata
```

### Bước 2: Cấu hình IP addresses

Copy file `.env.example` thành `.env` và cập nhật IP addresses cho từng node:

```bash
cp .env.example .env
nano .env
```

Cập nhật các IP addresses:
```env
# Node 1: Airflow + Redis (Celery)
NODE1_IP=192.168.1.10

# Node 2: Camera Producer + Kafka Broker
NODE2_IP=192.168.1.11

# Node 3: Spark Streaming Processor
NODE3_IP=192.168.1.12

# Node 4: Cassandra Database
NODE4_IP=192.168.1.13

# Node 5: Redis (Realtime Cache)
NODE5_IP=192.168.1.14

# Node 6: Streamlit Dashboard
NODE6_IP=192.168.1.15
```

### Bước 3: Copy project lên các máy worker

Copy toàn bộ thư mục `bigdata` lên từng máy worker:

```bash
# Trên máy master
scp -r bigdata/ user@node1-ip:/home/user/
scp -r bigdata/ user@node2-ip:/home/user/
# ... lặp lại cho các node khác
```

### Bước 4: Chạy từng node

Trên mỗi máy, chạy node tương ứng:

#### Node 1 - Airflow + Redis (Celery)
```bash
cd bigdata
NODE_TYPE=node1 docker-compose --profile node1 up -d
```

#### Node 2 - Camera Producer + Kafka
```bash
cd bigdata
NODE_TYPE=node2 docker-compose --profile node2 up -d
```

#### Node 3 - Spark Streaming
```bash
cd bigdata
NODE_TYPE=node3 docker-compose --profile node3 up -d
```

#### Node 4 - Cassandra
```bash
cd bigdata
NODE_TYPE=node4 docker-compose --profile node4 up -d

# Sau khi Cassandra khởi động, tạo schema:
docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/schema.cql
# Hoặc thủ công:
docker exec -it parking-cassandra cqlsh
# Sau đó chạy lệnh trong cassandra/schema.cql
```

#### Node 5 - Redis Cache
```bash
cd bigdata
NODE_TYPE=node5 docker-compose --profile node5 up -d
```

#### Node 6 - Streamlit Dashboard
```bash
cd bigdata
NODE_TYPE=node6 docker-compose --profile node6 up -d
```

### Bước 5: Khởi tạo Cassandra Schema

Trên Node 4, sau khi Cassandra đã khởi động:

```bash
docker exec -it parking-cassandra cqlsh
```

Chạy lệnh trong file `cassandra/schema.cql`:

```sql
CREATE KEYSPACE IF NOT EXISTS parking_system
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE parking_system;

CREATE TABLE IF NOT EXISTS parking_history (
    timestamp TIMESTAMP,
    license_plate TEXT,
    location TEXT,
    status_code TEXT,
    parking_duration_minutes DECIMAL,
    parking_fee DECIMAL,
    PRIMARY KEY ((license_plate), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

## 🚀 Sử dụng

### Kiểm tra trạng thái

1. **Kafka**: Kiểm tra topic `parking-events`
   ```bash
   docker exec -it parking-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic parking-events
   ```

2. **Spark Streaming**: Xem logs
   ```bash
   docker logs -f parking-spark-master
   ```

3. **Redis Cache**: Kiểm tra keys
   ```bash
   docker exec -it parking-redis-cache redis-cli -n 2
   > KEYS parking:*
   ```

4. **Dashboard**: Truy cập `http://NODE6_IP:8501`

5. **Airflow**: Truy cập `http://NODE1_IP:8080` (username/password: airflow/airflow)

## 💰 Tính tiền đỗ xe

Hệ thống tính tiền theo công thức:
- **1 phút = 10,000 VNĐ**
- Tính chính xác theo phút (có thể có số thập phân)
- Ví dụ: Đỗ 15 phút 30 giây = 15.5 phút = 155,000 VNĐ

## 📊 Kiến trúc

```
┌─────────────┐
│   Node 1    │  Airflow + Redis (Celery)
└─────────────┘
       │
       ├─────────────────────────────────┐
       │                                 │
┌─────────────┐                   ┌─────────────┐
│   Node 2    │                   │   Node 3    │
│ Camera +    │ ──Kafka──>        │   Spark     │
│   Kafka     │                   │ Streaming   │
└─────────────┘                   └─────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
            │   Node 4    │     │   Node 5    │     │   Node 6    │
            │  Cassandra  │     │   Redis     │     │ Dashboard   │
            │  (History)  │     │  (Realtime) │     │  (GUI)      │
            └─────────────┘     └─────────────┘     └─────────────┘
```

## 🔍 Troubleshooting

### Kafka không nhận được messages
- Kiểm tra Kafka broker đang chạy: `docker ps | grep kafka`
- Kiểm tra producer logs: `docker logs parking-camera-producer`

### Spark không xử lý được data
- Kiểm tra Spark logs: `docker logs parking-spark-master`
- Kiểm tra Kafka connection từ Spark
- Kiểm tra Redis connection

### Dashboard không hiển thị data
- Kiểm tra Redis connection
- Kiểm tra Redis có data: `docker exec parking-redis-cache redis-cli -n 2 KEYS parking:*`
- Kiểm tra dashboard logs: `docker logs parking-dashboard`

### Cassandra connection error
- Đợi Cassandra khởi động hoàn tất (có thể mất 30-60 giây)
- Kiểm tra schema đã được tạo chưa
- Kiểm tra Cassandra logs: `docker logs parking-cassandra`

## 📝 Files quan trọng

- `docker-compose.yml`: Cấu hình Docker cho tất cả nodes
- `.env`: Cấu hình IP addresses và ports
- `producer/camera_producer.py`: Camera Producer gửi events lên Kafka
- `spark/spark_streaming.py`: Spark Streaming xử lý và tính tiền
- `dashboard/app.py`: Streamlit Dashboard
- `cassandra/schema.cql`: Cassandra database schema
- `airflow/dags/parking_system_dag.py`: Airflow DAG

## 📄 License

MIT

## 👨‍💻 Tác giả

Hệ thống được phát triển cho bài tập Big Data - Distributed System

# BigData-ParkingSystem
