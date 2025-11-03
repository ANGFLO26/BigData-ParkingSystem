# ✅ CHECKLIST KIỂM TRA HỆ THỐNG

## 🔍 Kiểm tra Cấu hình

### 1. File .env
- [ ] Đã copy `.env.example` thành `.env` 
- [ ] Đã cập nhật IP addresses cho 6 nodes:
  - NODE1_IP (Airflow)
  - NODE2_IP (Kafka)
  - NODE3_IP (Spark)
  - NODE4_IP (Cassandra)
  - NODE5_IP (Redis Cache)
  - NODE6_IP (Dashboard)
- [ ] Đã cập nhật KAFKA_BOOTSTRAP_SERVERS = ${NODE2_IP}:9092
- [ ] Đã cập nhật REDIS_CACHE_HOST = ${NODE5_IP}
- [ ] Đã cập nhật CASSANDRA_HOST = ${NODE4_IP}

### 2. Docker và Docker Compose
- [ ] Docker đã cài đặt: `docker --version`
- [ ] Docker Compose đã cài đặt: `docker-compose --version`
- [ ] Docker daemon đang chạy: `docker ps`
- [ ] Không có container nào đang chiếm ports:
  - 2181 (Zookeeper)
  - 9092 (Kafka)
  - 6379 (Redis)
  - 9042 (Cassandra)
  - 8080 (Airflow/Spark UI)
  - 8501 (Dashboard)

### 3. Network
- [ ] Tất cả các máy trong cùng mạng LAN
- [ ] Có thể ping giữa các máy: `ping <NODE_IP>`
- [ ] Firewall đã mở các ports cần thiết
- [ ] IP addresses trong .env khớp với IP thực của từng máy

## 📦 Kiểm tra Files

### 4. Cấu trúc thư mục
```
bigdata/
├── docker-compose.yml ✅
├── .env ✅
├── producer/
│   ├── camera_producer.py ✅
│   ├── Dockerfile ✅
│   └── requirements.txt ✅
├── spark/
│   ├── spark_streaming.py ✅
│   └── Dockerfile.master ✅
├── cassandra/
│   ├── schema.cql ✅
│   └── init/create-tables.cql ✅
├── redis/
│   └── redis.conf ✅
├── dashboard/
│   ├── app.py ✅
│   ├── Dockerfile ✅
│   └── requirements.txt ✅
└── airflow/
    ├── Dockerfile ✅
    └── dags/parking_system_dag.py ✅
```

### 5. Dependencies
- [ ] `producer/requirements.txt`: kafka-python
- [ ] `spark/Dockerfile.master`: redis, cassandra-driver
- [ ] `dashboard/requirements.txt`: streamlit, redis, pandas

## 🚀 Kiểm tra khi Deploy

### 6. Node 2 (Kafka) - CHẠY ĐẦU TIÊN
- [ ] Zookeeper khởi động thành công
- [ ] Kafka khởi động thành công
- [ ] Camera Producer đang gửi events
- [ ] Có thể consume từ Kafka:
  ```bash
  docker exec -it parking-kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic parking-events
  ```

### 7. Node 5 (Redis Cache)
- [ ] Redis container đang chạy
- [ ] Có thể connect: `docker exec -it parking-redis-cache redis-cli -n 2 PING`
- [ ] Port 6379 đã expose

### 8. Node 4 (Cassandra)
- [ ] Cassandra container đang chạy (đợi 30-60 giây)
- [ ] Health check pass: `docker exec parking-cassandra nodetool status`
- [ ] Schema đã được tạo:
  ```bash
  docker exec -it parking-cassandra cqlsh
  DESCRIBE KEYSPACE parking_system;
  ```

### 9. Node 3 (Spark)
- [ ] Spark Master đang chạy
- [ ] Spark Streaming job đang chạy
- [ ] Logs không có lỗi kết nối Kafka
- [ ] Logs không có lỗi kết nối Redis
- [ ] Có thể truy cập Spark UI: http://NODE3_IP:4040

### 10. Node 6 (Dashboard)
- [ ] Dashboard container đang chạy
- [ ] Có thể truy cập: http://NODE6_IP:8501
- [ ] Dashboard hiển thị dữ liệu từ Redis
- [ ] Auto-refresh hoạt động

### 11. Node 1 (Airflow)
- [ ] PostgreSQL đang chạy
- [ ] Airflow webserver đang chạy
- [ ] Airflow scheduler đang chạy
- [ ] Có thể truy cập: http://NODE1_IP:8080
- [ ] DAG `parking_system_monitor` xuất hiện

## 🔗 Kiểm tra Kết nối

### 12. Kafka → Spark
- [ ] Spark logs hiển thị: "Spark Streaming started!"
- [ ] Spark logs hiển thị: "Waiting for data from Kafka..."
- [ ] Spark nhận được events và xử lý

### 13. Spark → Redis
- [ ] Spark logs hiển thị: "✅ Redis cache updated"
- [ ] Redis có keys: `parking:occupied_count`, `parking:location:*`

### 14. Spark → Cassandra
- [ ] Khi xe EXITING, Spark logs hiển thị: "💰 Xe ... tại ...: Đỗ ... phút, Phí: ..."
- [ ] Cassandra có data trong `parking_history` table

### 15. Redis → Dashboard
- [ ] Dashboard đọc được từ Redis
- [ ] Hiển thị số vị trí có xe/trống
- [ ] Hiển thị thông tin từng vị trí

## 💰 Kiểm tra Logic Tính tiền

### 16. Tính tiền đúng
- [ ] 1 phút = 10,000 VNĐ
- [ ] Tính chính xác theo phút (có thể có số thập phân)
- [ ] Ví dụ: 15.5 phút = 155,000 VNĐ
- [ ] Cập nhật realtime khi xe đang đỗ

## 📊 Kiểm tra End-to-End

### 17. Flow hoàn chỉnh
1. [ ] Producer gửi event ENTERING → Kafka
2. [ ] Spark nhận event ENTERING
3. [ ] Producer gửi event PARKED → Kafka
4. [ ] Spark nhận event PARKED, lưu start_time
5. [ ] Spark tính tiền realtime, update Redis
6. [ ] Dashboard hiển thị xe đang đỗ với thông tin tiền
7. [ ] Producer gửi event EXITING → Kafka
8. [ ] Spark nhận event EXITING, tính tiền cuối, lưu vào Cassandra
9. [ ] Dashboard cập nhật, vị trí thành trống

## 🐛 Troubleshooting Checklist

### Nếu Producer không gửi được:
- [ ] Kafka đang chạy?
- [ ] Topic `parking-events` đã được tạo?
- [ ] Producer logs có lỗi gì?

### Nếu Spark không nhận được data:
- [ ] KAFKA_BOOTSTRAP_SERVERS đúng IP Node 2?
- [ ] Kafka đang expose port 9092?
- [ ] Firewall cho phép kết nối?

### Nếu Redis không có data:
- [ ] Spark đang chạy và xử lý?
- [ ] REDIS_CACHE_HOST đúng IP Node 5?
- [ ] Redis container đang chạy?

### Nếu Dashboard trống:
- [ ] Redis có data không?
- [ ] REDIS_CACHE_HOST trong .env của Node 6 đúng không?
- [ ] Dashboard logs có lỗi gì?

## ✅ Final Check

- [ ] Tất cả 6 nodes đang chạy
- [ ] Data flow hoạt động: Kafka → Spark → Redis/Cassandra → Dashboard
- [ ] Tính tiền đúng theo yêu cầu
- [ ] Dashboard hiển thị đầy đủ thông tin
- [ ] Không có lỗi trong logs của các services

---

**Lưu ý**: Đánh dấu ✅ khi hoàn thành từng bước. Nếu có vấn đề, xem phần Troubleshooting hoặc logs của service tương ứng.

