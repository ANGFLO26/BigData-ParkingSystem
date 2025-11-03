# 📦 Hướng dẫn Deploy trên Nhiều Máy

Hướng dẫn chi tiết để deploy hệ thống đỗ xe trên 6 máy Ubuntu riêng biệt.

## 🔧 Chuẩn bị

### Yêu cầu cho mỗi máy:
- Ubuntu 20.04+ hoặc tương đương
- Docker Engine 20.10+
- Docker Compose 2.0+
- Tất cả máy trong cùng mạng LAN
- Tối thiểu 2GB RAM mỗi máy (khuyến nghị 4GB+)

### Network Setup:
- Đảm bảo tất cả các máy có thể ping được nhau
- Firewall cho phép các ports sau:
  - 2181 (Zookeeper)
  - 9092 (Kafka)
  - 6379 (Redis)
  - 9042 (Cassandra)
  - 8080, 7077 (Spark/Airflow)
  - 8501 (Dashboard)

## 📋 Bước 1: Setup trên Máy Master

1. **Clone hoặc copy project:**
```bash
cd ~
git clone <repository> bigdata
cd bigdata
```

2. **Tạo file .env:**
```bash
cp .env.example .env
nano .env
```

Cập nhật các IP addresses:
```env
NODE1_IP=192.168.1.10
NODE2_IP=192.168.1.11
NODE3_IP=192.168.1.12
NODE4_IP=192.168.1.13
NODE5_IP=192.168.1.14
NODE6_IP=192.168.1.15
```

## 📦 Bước 2: Copy Project lên Các Máy Worker

### Option 1: Sử dụng SCP
```bash
# Copy lên Node 1
scp -r bigdata/ user@192.168.1.10:/home/user/

# Copy lên Node 2
scp -r bigdata/ user@192.168.1.11:/home/user/

# ... lặp lại cho các node khác
```

### Option 2: Sử dụng Git
Trên mỗi máy worker:
```bash
git clone <repository>
cd bigdata
cp .env.example .env
# Cập nhật .env với IP đúng
```

## 🚀 Bước 3: Deploy từng Node

### Node 2: Kafka + Producer (CHẠY ĐẦU TIÊN)
```bash
ssh user@192.168.1.11
cd bigdata
docker-compose --profile node2 up -d

# Kiểm tra Kafka đã sẵn sàng
docker logs -f parking-kafka
# Đợi thấy message "started"
```

### Node 5: Redis Cache
```bash
ssh user@192.168.1.14
cd bigdata
docker-compose --profile node5 up -d

# Test Redis
docker exec -it parking-redis-cache redis-cli -n 2 PING
# Kết quả: PONG
```

### Node 4: Cassandra
```bash
ssh user@192.168.1.13
cd bigdata
docker-compose --profile node4 up -d

# Đợi Cassandra khởi động (30-60 giây)
sleep 60

# Tạo schema
docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/create-tables.cql

# Hoặc thủ công:
docker exec -it parking-cassandra cqlsh
# Copy paste nội dung từ cassandra/schema.cql
```

### Node 3: Spark Streaming
```bash
ssh user@192.168.1.12
cd bigdata

# Đảm bảo .env có đúng IP của Kafka, Redis, Cassandra
docker-compose --profile node3 up -d

# Kiểm tra logs
docker logs -f parking-spark-master
# Đợi thấy "Spark Streaming started!"
```

### Node 6: Dashboard
```bash
ssh user@192.168.1.15
cd bigdata
docker-compose --profile node6 up -d

# Truy cập: http://192.168.1.15:8501
```

### Node 1: Airflow
```bash
ssh user@192.168.1.10
cd bigdata
docker-compose --profile node1 up -d

# Đợi Airflow khởi động (1-2 phút)
# Truy cập: http://192.168.1.10:8080
# Username/Password: airflow/airflow
```

## ✅ Bước 4: Kiểm tra Hệ thống

### 1. Kiểm tra Producer gửi data:
```bash
# Trên Node 2
docker logs parking-camera-producer
# Phải thấy: "✅ Event #X sent: ..."
```

### 2. Kiểm tra Kafka nhận messages:
```bash
# Trên Node 2
docker exec -it parking-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic parking-events \
  --from-beginning
```

### 3. Kiểm tra Spark xử lý:
```bash
# Trên Node 3
docker logs parking-spark-master
# Phải thấy: "✅ Redis cache updated: X occupied"
```

### 4. Kiểm tra Redis có data:
```bash
# Trên Node 5
docker exec -it parking-redis-cache redis-cli -n 2
> KEYS parking:*
> GET parking:occupied_count
> GET parking:location:A1
```

### 5. Kiểm tra Dashboard:
Mở trình duyệt: `http://NODE6_IP:8501`
- Phải thấy tổng quan số vị trí
- Phải thấy các xe đang đỗ với thông tin tiền

## 🔍 Troubleshooting

### Lỗi: Kafka không connect được
**Nguyên nhân:** IP không đúng trong .env
**Giải pháp:** 
- Kiểm tra `NODE2_IP` trong .env của Node 3
- Kiểm tra `KAFKA_BOOTSTRAP_SERVERS` có đúng không

### Lỗi: Redis connection timeout
**Nguyên nhân:** Firewall block port 6379
**Giải pháp:**
```bash
sudo ufw allow 6379/tcp
```

### Lỗi: Spark không nhận được data từ Kafka
**Nguyên nhân:** Kafka chưa expose đúng IP
**Giải pháp:**
- Trong docker-compose.yml của Node 2, đảm bảo `KAFKA_ADVERTISED_LISTENERS` có IP của Node 2
- Restart Kafka: `docker-compose restart kafka`

### Lỗi: Dashboard không hiển thị data
**Nguyên nhân:** Redis connection error
**Giải pháp:**
- Kiểm tra `REDIS_CACHE_HOST` trong .env của Node 6
- Test connection: `docker exec parking-dashboard ping ${REDIS_CACHE_HOST}`

## 📊 Thứ tự khởi động đúng:

1. **Node 2** (Kafka) - Phải chạy đầu tiên
2. **Node 5** (Redis) - Có thể chạy song song
3. **Node 4** (Cassandra) - Cần thời gian khởi động
4. **Node 3** (Spark) - Sau khi Kafka, Redis, Cassandra đã sẵn sàng
5. **Node 6** (Dashboard) - Cần Redis sẵn sàng
6. **Node 1** (Airflow) - Có thể chạy cuối cùng

## 🔄 Script tự động:

Tạo file `deploy-all.sh` trên máy master:

```bash
#!/bin/bash
# Deploy all nodes (chạy từ máy master, SSH vào các máy khác)

NODES=(
    "user@192.168.1.11:2"
    "user@192.168.1.14:5"
    "user@192.168.1.13:4"
    "user@192.168.1.12:3"
    "user@192.168.1.15:6"
    "user@192.168.1.10:1"
)

for node_info in "${NODES[@]}"; do
    IFS=':' read -r user_host node_num <<< "$node_info"
    echo "🚀 Deploying Node $node_num on $user_host..."
    ssh "$user_host" "cd bigdata && docker-compose --profile node$node_num up -d"
done
```

Chạy:
```bash
chmod +x deploy-all.sh
./deploy-all.sh
```

## 📝 Lưu ý:

1. **IP Address:** Đảm bảo các IP trong .env khớp với IP thực của từng máy
2. **Network:** Tất cả máy phải trong cùng subnet
3. **Ports:** Mở firewall cho các ports cần thiết
4. **Thứ tự:** Tuân thủ thứ tự khởi động ở trên
5. **Timing:** Đợi các service khởi động xong trước khi chạy service phụ thuộc

