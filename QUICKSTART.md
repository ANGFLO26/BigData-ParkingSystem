# ⚡ Quick Start Guide

Hướng dẫn nhanh để chạy hệ thống đỗ xe.

## 🚀 Các bước nhanh

### 1. Setup trên mỗi máy

```bash
# Clone project (hoặc copy từ máy master)
cd ~
cd bigdata

# Copy .env.example thành .env và cập nhật IP
cp .env.example .env
nano .env  # Cập nhật IP addresses
```

### 2. Chạy từng node (theo thứ tự)

**Node 2 (Kafka) - CHẠY ĐẦU TIÊN:**
```bash
./start-node.sh 2
# Hoặc: docker-compose --profile node2 up -d
```

**Node 5 (Redis):**
```bash
./start-node.sh 5
```

**Node 4 (Cassandra):**
```bash
./start-node.sh 4
# Sau 60 giây, tạo schema:
docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/create-tables.cql
```

**Node 3 (Spark):**
```bash
./start-node.sh 3
# Kiểm tra logs:
docker logs -f parking-spark-master
```

**Node 6 (Dashboard):**
```bash
./start-node.sh 6
# Truy cập: http://YOUR_NODE6_IP:8501
```

**Node 1 (Airflow):**
```bash
./start-node.sh 1
# Truy cập: http://YOUR_NODE1_IP:8080
```

### 3. Kiểm tra

**Xem producer đang gửi events:**
```bash
docker logs -f parking-camera-producer
```

**Xem Spark đang xử lý:**
```bash
docker logs -f parking-spark-master
```

**Xem Dashboard:**
- Mở trình duyệt: `http://NODE6_IP:8501`
- Phải thấy các xe đang đỗ và thông tin tiền

### 4. Dừng hệ thống

```bash
# Dừng từng node
./stop-node.sh 2
./stop-node.sh 5
# ... hoặc dừng tất cả:
docker-compose --profile all down
```

## ✅ Checklist

- [ ] Node 2 (Kafka) đang chạy
- [ ] Node 5 (Redis) đang chạy
- [ ] Node 4 (Cassandra) đã khởi động và có schema
- [ ] Node 3 (Spark) đang xử lý events
- [ ] Node 6 (Dashboard) hiển thị dữ liệu
- [ ] Producer đang gửi events lên Kafka

## 🐛 Troubleshooting nhanh

**Producer không gửi được:**
```bash
docker logs parking-camera-producer
# Kiểm tra KAFKA_BOOTSTRAP_SERVERS trong .env
```

**Spark không nhận được data:**
```bash
docker logs parking-spark-master
# Kiểm tra KAFKA_BOOTSTRAP_SERVERS và REDIS_CACHE_HOST
```

**Dashboard trống:**
```bash
# Kiểm tra Redis có data:
docker exec -it parking-redis-cache redis-cli -n 2 KEYS parking:*
# Kiểm tra REDIS_CACHE_HOST trong .env của Node 6
```

