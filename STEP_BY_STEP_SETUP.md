# 🚀 Hướng Dẫn Setup Từng Bước - Không Cần Chỉnh Code

Hướng dẫn chi tiết để setup hệ thống trên từng worker, **KHÔNG CẦN CHỈNH CODE**, chỉ cần cấu hình IP.

## 📋 Chuẩn Bị

### Yêu cầu trên mỗi máy:
- Ubuntu 20.04+ 
- Docker đã cài: `docker --version`
- Docker Compose đã cài: `docker-compose --version`
- Tất cả máy trong cùng mạng LAN (192.168.80.x)

### IP của bạn:
- **Máy Master**: 192.168.80.84
- **Node 1 (Airflow)**: 192.168.80.84 (cùng máy master)
- **Node 2 (Kafka)**: Thay bằng IP thực của máy Node 2
- **Node 3 (Spark)**: Thay bằng IP thực của máy Node 3
- **Node 4 (Cassandra)**: Thay bằng IP thực của máy Node 4
- **Node 5 (Redis)**: Thay bằng IP thực của máy Node 5
- **Node 6 (Dashboard)**: Thay bằng IP thực của máy Node 6

---

## BƯỚC 1: Setup trên Máy Master (192.168.80.84)

### 1.1. Kiểm tra code đã có
```bash
cd ~/Documents/bigdata
ls -la
# Phải thấy: docker-compose.yml, producer/, spark/, dashboard/, ...
```

### 1.2. Tạo file .env cho máy master (Node 1)
```bash
cd ~/Documents/bigdata

# Chạy script tự động
./setup-env.sh

# Hoặc tạo thủ công:
cat > .env << 'EOF'
MASTER_IP=192.168.80.84

NODE1_IP=192.168.80.84
REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

# CẬP NHẬT IP CÁC MÁY WORKER Ở ĐÂY:
NODE2_IP=192.168.80.85    # <-- SỬA THÀNH IP THỰC CỦA MÁY NODE 2
NODE3_IP=192.168.80.86    # <-- SỬA THÀNH IP THỰC CỦA MÁY NODE 3
NODE4_IP=192.168.80.87    # <-- SỬA THÀNH IP THỰC CỦA MÁY NODE 4
NODE5_IP=192.168.80.88    # <-- SỬA THÀNH IP THỰC CỦA MÁY NODE 5
NODE6_IP=192.168.80.89    # <-- SỬA THÀNH IP THỰC CỦA MÁY NODE 6

KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000
REDIS_CACHE_PORT=6379
REDIS_DB=2
DASHBOARD_PORT=8501
PRICE_PER_MINUTE=10000

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT}
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=${CASSANDRA_PORT}
EOF
```

### 1.3. Kiểm tra file .env
```bash
cat .env | grep "NODE.*IP"
# Phải thấy đầy đủ 6 nodes
```

### 1.4. Copy code lên các máy worker
```bash
# Giả sử username là "user" và máy worker ở /home/user/bigdata
# Copy lên Node 2
scp -r ~/Documents/bigdata/ user@192.168.80.85:/home/user/

# Copy lên Node 3
scp -r ~/Documents/bigdata/ user@192.168.80.86:/home/user/

# Copy lên Node 4
scp -r ~/Documents/bigdata/ user@192.168.80.87:/home/user/

# Copy lên Node 5
scp -r ~/Documents/bigdata/ user@192.168.80.88:/home/user/

# Copy lên Node 6
scp -r ~/Documents/bigdata/ user@192.168.80.89:/home/user/
```

**Lưu ý**: Thay `user` và IP cho đúng với môi trường của bạn!

---

## BƯỚC 2: Setup trên Node 2 (Kafka) - IP: 192.168.80.85

### 2.1. SSH vào máy Node 2
```bash
ssh user@192.168.80.85
```

### 2.2. Vào thư mục project
```bash
cd ~/bigdata
ls -la
# Phải thấy: docker-compose.yml, producer/, ...
```

### 2.3. Tạo file .env cho Node 2
```bash
cat > .env << 'EOF'
MASTER_IP=192.168.80.84

NODE1_IP=192.168.80.84
NODE2_IP=192.168.80.85    # <-- IP CỦA MÁY NÀY
NODE3_IP=192.168.80.86
NODE4_IP=192.168.80.87
NODE5_IP=192.168.80.88
NODE6_IP=192.168.80.89

KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000
REDIS_CACHE_PORT=6379
REDIS_DB=2
DASHBOARD_PORT=8501
PRICE_PER_MINUTE=10000

REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT}
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=${CASSANDRA_PORT}
EOF
```

**QUAN TRỌNG**: NODE2_IP phải là IP thực của máy này!

### 2.4. Kiểm tra network
```bash
# Test ping đến máy master
ping -c 2 192.168.80.84

# Test ping đến Node 5 (Redis) và Node 4 (Cassandra)
ping -c 2 192.168.80.88
ping -c 2 192.168.80.87
```

### 2.5. Chạy Node 2
```bash
cd ~/bigdata
docker-compose --profile node2 up -d

# Đợi 30 giây
sleep 30

# Kiểm tra containers đang chạy
docker ps | grep parking

# Xem logs
docker logs parking-kafka | tail -20
docker logs parking-camera-producer | tail -20
```

**Kỳ vọng**: 
- Zookeeper và Kafka đang chạy
- Camera Producer đang gửi events
- Logs hiển thị: "✅ Event #X sent: ..."

---

## BƯỚC 3: Setup trên Node 5 (Redis) - IP: 192.168.80.88

### 3.1. SSH vào máy Node 5
```bash
ssh user@192.168.80.88
```

### 3.2. Vào thư mục project
```bash
cd ~/bigdata
```

### 3.3. Tạo file .env cho Node 5
```bash
cat > .env << 'EOF'
MASTER_IP=192.168.80.84

NODE1_IP=192.168.80.84
NODE2_IP=192.168.80.85
NODE3_IP=192.168.80.86
NODE4_IP=192.168.80.87
NODE5_IP=192.168.80.88    # <-- IP CỦA MÁY NÀY
NODE6_IP=192.168.80.89

KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000
REDIS_CACHE_PORT=6379
REDIS_DB=2
DASHBOARD_PORT=8501
PRICE_PER_MINUTE=10000

REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT}
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=${CASSANDRA_PORT}
EOF
```

### 3.4. Chạy Node 5
```bash
docker-compose --profile node5 up -d

# Kiểm tra
docker ps | grep parking-redis-cache

# Test Redis
docker exec -it parking-redis-cache redis-cli -n 2 PING
# Phải trả về: PONG
```

---

## BƯỚC 4: Setup trên Node 4 (Cassandra) - IP: 192.168.80.87

### 4.1. SSH vào máy Node 4
```bash
ssh user@192.168.80.87
```

### 4.2. Vào thư mục và tạo .env
```bash
cd ~/bigdata

cat > .env << 'EOF'
MASTER_IP=192.168.80.84

NODE1_IP=192.168.80.84
NODE2_IP=192.168.80.85
NODE3_IP=192.168.80.86
NODE4_IP=192.168.80.87    # <-- IP CỦA MÁY NÀY
NODE5_IP=192.168.80.88
NODE6_IP=192.168.80.89

KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000
REDIS_CACHE_PORT=6379
REDIS_DB=2
DASHBOARD_PORT=8501
PRICE_PER_MINUTE=10000

REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT}
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=${CASSANDRA_PORT}
EOF
```

### 4.3. Chạy Node 4
```bash
docker-compose --profile node4 up -d

# Đợi 60 giây để Cassandra khởi động hoàn toàn
sleep 60

# Kiểm tra status
docker exec parking-cassandra nodetool status
# Phải thấy: UN (Up Normal)

# Tạo schema
docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/create-tables.cql

# Hoặc thủ công nếu lỗi:
docker exec -it parking-cassandra cqlsh
```

Trong cqlsh, chạy:
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

CREATE INDEX IF NOT EXISTS idx_location ON parking_history (location);
exit;
```

---

## BƯỚC 5: Setup trên Node 3 (Spark) - IP: 192.168.80.86

### 5.1. SSH vào máy Node 3
```bash
ssh user@192.168.80.86
```

### 5.2. Vào thư mục và tạo .env
```bash
cd ~/bigdata

cat > .env << 'EOF'
MASTER_IP=192.168.80.84

NODE1_IP=192.168.80.84
NODE2_IP=192.168.80.85    # QUAN TRỌNG: IP Kafka
NODE3_IP=192.168.80.86    # <-- IP CỦA MÁY NÀY
NODE4_IP=192.168.80.87    # QUAN TRỌNG: IP Cassandra
NODE5_IP=192.168.80.88    # QUAN TRỌNG: IP Redis
NODE6_IP=192.168.80.89

KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000
REDIS_CACHE_PORT=6379
REDIS_DB=2
DASHBOARD_PORT=8501
PRICE_PER_MINUTE=10000

REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

# QUAN TRỌNG: Phải đúng IP của Node 2 (Kafka)
KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
# QUAN TRỌNG: Phải đúng IP của Node 5 (Redis)
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT}
# QUAN TRỌNG: Phải đúng IP của Node 4 (Cassandra)
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=${CASSANDRA_PORT}
EOF
```

### 5.3. Kiểm tra kết nối đến Kafka, Redis, Cassandra
```bash
# Test ping
ping -c 2 192.168.80.85  # Kafka
ping -c 2 192.168.80.88  # Redis
ping -c 2 192.168.80.87  # Cassandra

# Test port (nếu có nc)
nc -zv 192.168.80.85 9092  # Kafka
nc -zv 192.168.80.88 6379  # Redis
nc -zv 192.168.80.87 9042  # Cassandra
```

### 5.4. Chạy Node 3
```bash
docker-compose --profile node3 up -d

# Đợi 30 giây
sleep 30

# Xem logs
docker logs parking-spark-master | tail -30

# Kiểm tra config
docker logs parking-spark-master | grep "Configuration"
# Phải thấy đúng IP: Kafka, Redis, Cassandra
```

**Kỳ vọng**:
- Spark đã connect được Kafka
- Logs hiển thị: "Spark Streaming started!"
- Logs hiển thị: "📦 Processing batch #X"

---

## BƯỚC 6: Setup trên Node 6 (Dashboard) - IP: 192.168.80.89

### 6.1. SSH vào máy Node 6
```bash
ssh user@192.168.80.89
```

### 6.2. Vào thư mục và tạo .env
```bash
cd ~/bigdata

cat > .env << 'EOF'
MASTER_IP=192.168.80.84

NODE1_IP=192.168.80.84
NODE2_IP=192.168.80.85
NODE3_IP=192.168.80.86
NODE4_IP=192.168.80.87
NODE5_IP=192.168.80.88    # QUAN TRỌNG: IP Redis
NODE6_IP=192.168.80.89    # <-- IP CỦA MÁY NÀY

KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000
REDIS_CACHE_PORT=6379
REDIS_DB=2
DASHBOARD_PORT=8501
PRICE_PER_MINUTE=10000

REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
# QUAN TRỌNG: Phải đúng IP của Node 5 (Redis)
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT}
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=${CASSANDRA_PORT}
EOF
```

### 6.3. Chạy Node 6
```bash
docker-compose --profile node6 up -d

# Đợi 10 giây
sleep 10

# Kiểm tra logs
docker logs parking-dashboard | tail -20

# Kiểm tra port
docker port parking-dashboard
# Phải thấy: 8501/tcp -> 0.0.0.0:8501
```

### 6.4. Truy cập Dashboard
Mở trình duyệt: `http://192.168.80.89:8501`

**Kỳ vọng**: Dashboard hiển thị, có dữ liệu từ Redis

---

## BƯỚC 7: Setup trên Node 1 (Airflow) - Máy Master (192.168.80.84)

### 7.1. Trên máy master
```bash
cd ~/Documents/bigdata

# Đảm bảo .env đã có (từ bước 1.2)
cat .env | grep NODE1_IP
```

### 7.2. Chạy Node 1
```bash
docker-compose --profile node1 up -d

# Đợi 2 phút để Airflow khởi động
sleep 120

# Kiểm tra
docker ps | grep parking-airflow

# Truy cập: http://192.168.80.84:8080
# Username/Password: airflow/airflow
```

---

## ✅ KIỂM TRA CUỐI CÙNG

### 1. Kiểm tra tất cả containers đang chạy

**Trên Node 2:**
```bash
docker ps | grep parking
# Phải thấy: parking-zookeeper, parking-kafka, parking-camera-producer
```

**Trên Node 3:**
```bash
docker ps | grep parking
# Phải thấy: parking-spark-master
```

**Trên Node 4:**
```bash
docker ps | grep parking
# Phải thấy: parking-cassandra
```

**Trên Node 5:**
```bash
docker ps | grep parking
# Phải thấy: parking-redis-cache
```

**Trên Node 6:**
```bash
docker ps | grep parking
# Phải thấy: parking-dashboard
```

**Trên Node 1 (Master):**
```bash
docker ps | grep parking
# Phải thấy: parking-redis-celery, parking-postgres, parking-airflow-*
```

### 2. Kiểm tra Data Flow

**Kiểm tra Producer đang gửi:**
```bash
# Trên Node 2
docker logs parking-camera-producer | tail -10
# Phải thấy: "✅ Event #X sent: ..."
```

**Kiểm tra Spark đang xử lý:**
```bash
# Trên Node 3
docker logs parking-spark-master | tail -10
# Phải thấy: "📦 Processing batch #X"
# Phải thấy: "✅ Redis cache updated"
```

**Kiểm tra Redis có data:**
```bash
# Trên Node 5
docker exec -it parking-redis-cache redis-cli -n 2
> KEYS parking:*
> GET parking:occupied_count
> exit
```

**Kiểm tra Dashboard:**
- Mở: `http://192.168.80.89:8501`
- Phải thấy: Tổng số vị trí, số vị trí có xe/trống
- Phải thấy: Bảng chi tiết các vị trí

---

## 🐛 Nếu Có Lỗi

### Lỗi: Không kết nối được Kafka
- Kiểm tra NODE2_IP trong .env của Node 3 có đúng không
- Kiểm tra Kafka đang chạy: `docker ps | grep kafka`
- Kiểm tra port 9092 đã expose: `docker port parking-kafka`

### Lỗi: Không kết nối được Redis
- Kiểm tra NODE5_IP trong .env của Node 3 và Node 6
- Kiểm tra Redis đang chạy: `docker ps | grep redis-cache`
- Test connection: `docker exec parking-redis-cache redis-cli -n 2 PING`

### Lỗi: Không kết nối được Cassandra
- Kiểm tra NODE4_IP trong .env của Node 3
- Kiểm tra Cassandra đang chạy: `docker exec parking-cassandra nodetool status`
- Đợi đủ 60 giây để Cassandra khởi động

### Lỗi: Dashboard trống
- Kiểm tra Redis có data: `docker exec parking-redis-cache redis-cli -n 2 KEYS parking:*`
- Kiểm tra REDIS_CACHE_HOST trong .env của Node 6
- Xem logs: `docker logs parking-dashboard`

---

## 📝 Checklist Hoàn Thành

- [ ] Node 2 (Kafka): Đang chạy, Producer đang gửi events
- [ ] Node 5 (Redis): Đang chạy, có thể connect
- [ ] Node 4 (Cassandra): Đang chạy, schema đã tạo
- [ ] Node 3 (Spark): Đang chạy, đang xử lý events
- [ ] Node 6 (Dashboard): Đang chạy, hiển thị dữ liệu
- [ ] Node 1 (Airflow): Đang chạy (optional)

---

## 🎉 Hoàn Thành!

Nếu tất cả các bước trên hoàn thành, hệ thống đã sẵn sàng!

**Không cần chỉnh code**, chỉ cần:
1. ✅ Copy code lên các máy
2. ✅ Tạo file .env với IP đúng
3. ✅ Chạy từng node theo thứ tự

**Chúc bạn thành công!** 🚀

