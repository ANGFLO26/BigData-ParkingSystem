# 📋 Tổng kết Dự án Hệ Thống Đỗ Xe Phân Tán

## ✅ Đã hoàn thành

### 1. Docker Infrastructure ✅
- **docker-compose.yml**: Cấu hình cho 6 nodes với profiles
- **.env.example**: Template cấu hình IP và ports
- **Scripts**: `start-node.sh`, `stop-node.sh` để quản lý nodes

### 2. Node 2: Camera Producer + Kafka ✅
- **camera_producer.py**: Convert từ code gốc, gửi events lên Kafka
- **Dockerfile**: Container cho producer
- **Kafka Broker**: Cấu hình với Zookeeper
- **Features**: 
  - Gửi parking events (ENTERING, PARKED, MOVING, EXITING)
  - Key-based partitioning (theo license_plate)
  - Auto-retry và error handling

### 3. Node 3: Spark Structured Streaming ✅
- **spark_streaming.py**: Xử lý realtime từ Kafka
- **Dockerfile.master**: Spark container với dependencies
- **Features**:
  - Stateful processing: Track parking duration
  - Tính tiền: 1 phút = 10,000 VNĐ (chính xác theo phút)
  - Ghi vào Redis (realtime) và Cassandra (history)
  - Watermarking và window processing

### 4. Node 4: Cassandra Database ✅
- **schema.cql**: Database schema
- **create-tables.cql**: Init script
- **Features**:
  - Keyspace: `parking_system`
  - Table: `parking_history` với indexing

### 5. Node 5: Redis Cache ✅
- **redis.conf**: Cấu hình Redis
- **Features**:
  - Database 2 (tách biệt với Celery)
  - TTL: 3600 giây
  - Cache realtime data cho dashboard

### 6. Node 6: Streamlit Dashboard ✅
- **app.py**: GUI hiển thị trạng thái realtime
- **Dockerfile**: Container cho Streamlit
- **Features**:
  - Bản đồ bãi đỗ (60 vị trí)
  - Hiển thị thông tin từng xe: biển số, thời gian đỗ, phí
  - Auto-refresh
  - Tổng doanh thu
  - Phân theo tầng (A, B, C, D, E, F)

### 7. Node 1: Airflow ✅
- **parking_system_dag.py**: DAG để monitor hệ thống
- **Dockerfile**: Airflow container
- **Features**:
  - Health checks cho các nodes
  - Generate reports định kỳ

### 8. Documentation ✅
- **README.md**: Hướng dẫn tổng quan
- **DEPLOYMENT.md**: Hướng dẫn deploy chi tiết
- **QUICKSTART.md**: Hướng dẫn nhanh
- **ARCHITECTURE.md**: Kiến trúc hệ thống
- **PLAN.md**: Kế hoạch ban đầu

## 🎯 Yêu cầu đã đáp ứng

✅ **Tính tiền đỗ xe**: 1 phút = 10,000 VNĐ (tính chính xác theo phút)  
✅ **Thông báo vị trí có xe/trống**: Dashboard hiển thị realtime  
✅ **Thông tin chi tiết**: Biển số, thời gian đỗ, phí cho mỗi vị trí  
✅ **Streaming lên Kafka**: Producer gửi events lên Kafka  
✅ **Spark Stateful**: Xử lý stateful với window và watermark  
✅ **Chạy phân tán**: 6 nodes trên 6 máy Ubuntu riêng biệt  
✅ **Docker setup**: Dễ dàng deploy trên nhiều máy  

## 📁 Cấu trúc Project

```
bigdata/
├── docker-compose.yml          # Main orchestration
├── .env.example                # Environment template
├── README.md                   # Documentation chính
├── DEPLOYMENT.md              # Hướng dẫn deploy
├── QUICKSTART.md              # Quick start
├── ARCHITECTURE.md            # Kiến trúc
├── SUMMARY.md                  # File này
│
├── producer/                   # Node 2
│   ├── camera_producer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── spark/                      # Node 3
│   ├── spark_streaming.py
│   └── Dockerfile.master
│
├── cassandra/                  # Node 4
│   ├── schema.cql
│   └── init/create-tables.cql
│
├── redis/                      # Node 5
│   └── redis.conf
│
├── dashboard/                  # Node 6
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── airflow/                    # Node 1
    ├── Dockerfile
    └── dags/parking_system_dag.py
```

## 🔧 Tính năng chính

### Tính tiền đỗ xe
- **Công thức**: `fee = (duration_seconds / 60.0) * 10000`
- **Ví dụ**: 15 phút 30 giây = 15.5 phút = 155,000 VNĐ
- **Tính realtime**: Cập nhật liên tục khi xe đang đỗ

### Stateful Processing
- Track state mỗi xe (license_plate, location, start_time)
- Xử lý status transitions: ENTERING → PARKED → MOVING → EXITING
- Watermarking để xử lý late events

### Realtime Dashboard
- 60 vị trí đỗ (6 tầng × 10 vị trí/tầng)
- Hiển thị realtime với auto-refresh
- Phân loại theo tầng
- Tổng hợp doanh thu

## 🚀 Cách sử dụng

1. **Setup trên máy master:**
   ```bash
   cd bigdata
   cp .env.example .env
   # Cập nhật IP addresses
   ```

2. **Copy lên các máy worker:**
   ```bash
   scp -r bigdata/ user@node-ip:/home/user/
   ```

3. **Chạy từng node:**
   ```bash
   ./start-node.sh 2  # Kafka (chạy đầu tiên)
   ./start-node.sh 5  # Redis
   ./start-node.sh 4  # Cassandra (tạo schema sau khi khởi động)
   ./start-node.sh 3  # Spark
   ./start-node.sh 6  # Dashboard
   ./start-node.sh 1  # Airflow
   ```

4. **Truy cập Dashboard:**
   - URL: `http://NODE6_IP:8501`

## ⚠️ Lưu ý quan trọng

1. **Thứ tự khởi động**: Kafka → Redis/Cassandra → Spark → Dashboard → Airflow
2. **IP Configuration**: Phải cập nhật đúng IP trong `.env` cho từng node
3. **Cassandra Schema**: Phải tạo schema sau khi Cassandra khởi động
4. **Network**: Tất cả máy phải trong cùng mạng LAN
5. **Firewall**: Mở các ports cần thiết (9092, 6379, 9042, 8501, 8080)

## 🔍 Testing

### Test Producer
```bash
docker logs -f parking-camera-producer
```

### Test Kafka
```bash
docker exec -it parking-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic parking-events \
  --from-beginning
```

### Test Redis
```bash
docker exec -it parking-redis-cache redis-cli -n 2
> KEYS parking:*
> GET parking:occupied_count
```

### Test Spark
```bash
docker logs -f parking-spark-master
```

## 📊 Metrics & Monitoring

- **Kafka**: Messages/second, lag
- **Spark**: Processing rate, checkpoint
- **Redis**: Keys count, memory usage
- **Dashboard**: Occupancy rate, revenue

## 🎓 Demo Checklist

Trước khi demo trên lớp:

- [ ] Tất cả 6 nodes đang chạy
- [ ] Producer đang gửi events
- [ ] Spark đang xử lý
- [ ] Dashboard hiển thị dữ liệu
- [ ] Có thể thấy xe vào đỗ và tính tiền realtime
- [ ] Có thể thấy xe ra và lưu vào Cassandra
- [ ] Airflow DAG chạy thành công

## 📝 Báo cáo cần có

1. **Kiến trúc hệ thống**: Diagram và giải thích
2. **Code walkthrough**: Giải thích các components
3. **Demo**: Chạy live và giải thích
4. **Kết quả**: Screenshots và metrics

## 🔗 Resources

- Kafka: https://kafka.apache.org/
- Spark: https://spark.apache.org/
- Redis: https://redis.io/
- Cassandra: https://cassandra.apache.org/
- Streamlit: https://streamlit.io/
- Airflow: https://airflow.apache.org/

---

**Tác giả**: Sinh viên Big Data  
**Ngày tạo**: 2024  
**Mục đích**: Bài tập hệ thống Big Data phân tán

