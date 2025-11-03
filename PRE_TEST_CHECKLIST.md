# ✅ CHECKLIST TRƯỚC KHI TEST

## 🎯 Tổng quan

Hệ thống đã được kiểm tra và **SẴN SÀNG** để test. Dưới đây là checklist cuối cùng.

## ✅ Đã Kiểm Tra

### 1. Code Files ✅
- [x] `producer/camera_producer.py` - Gửi events lên Kafka
- [x] `spark/spark_streaming.py` - Xử lý và tính tiền
- [x] `dashboard/app.py` - GUI hiển thị
- [x] `airflow/dags/parking_system_dag.py` - Monitoring
- [x] Không có linter errors

### 2. Dependencies ✅
- [x] `producer/requirements.txt` - kafka-python
- [x] `dashboard/requirements.txt` - streamlit, redis, pandas
- [x] `spark/Dockerfile.master` - redis, cassandra-driver, Kafka connector JARs

### 3. Docker Configuration ✅
- [x] `docker-compose.yml` - 6 nodes với profiles
- [x] Networks và volumes được cấu hình
- [x] Environment variables được truyền đúng
- [x] Ports không conflict (chạy trên máy khác nhau)

### 4. Database Schemas ✅
- [x] `cassandra/schema.cql` - Keyspace và tables
- [x] `cassandra/init/create-tables.cql` - Init script
- [x] `redis/redis.conf` - Redis configuration

### 5. Logic Tính tiền ✅
- [x] Công thức đúng: `fee = (duration_seconds / 60.0) * 10000`
- [x] Tính chính xác theo phút (15.5 phút = 155,000 VNĐ)
- [x] Cập nhật realtime khi đỗ
- [x] Lưu vào Cassandra khi xe ra

### 6. Documentation ✅
- [x] README.md - Hướng dẫn tổng quan
- [x] DEPLOYMENT.md - Hướng dẫn deploy
- [x] QUICKSTART.md - Quick start
- [x] ARCHITECTURE.md - Kiến trúc hệ thống
- [x] CHECKLIST.md - Checklist kiểm tra
- [x] TESTING_GUIDE.md - Hướng dẫn test
- [x] VALIDATION_REPORT.md - Báo cáo validation

## ⚠️ CẦN LÀM TRƯỚC KHI TEST

### 1. Tạo file .env (QUAN TRỌNG!)

**Với IP máy master: 192.168.80.84**

```bash
cd bigdata
cp .env.template .env
nano .env  # Sửa IP cho đúng
```

Hoặc tạo thủ công:
```bash
cat > .env << 'EOF'
# Máy Master IP
MASTER_IP=192.168.80.84

# Các Nodes (sửa IP cho đúng với từng máy)
NODE1_IP=192.168.80.84  # Master (Airflow)
NODE2_IP=192.168.80.85  # Kafka
NODE3_IP=192.168.80.86  # Spark
NODE4_IP=192.168.80.87  # Cassandra
NODE5_IP=192.168.80.88  # Redis
NODE6_IP=192.168.80.89  # Dashboard

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=6379
REDIS_DB=2
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=9042
PRICE_PER_MINUTE=10000
KAFKA_TOPIC=parking-events
EOF
```

**QUAN TRỌNG**: 
- Nếu test trên cùng máy master: Sửa tất cả IP thành `192.168.80.84`
- Nếu phân tán: Sửa IP cho đúng với từng máy worker

**Xem thêm**: `SETUP_WITH_MASTER_IP.md` để biết cách setup với IP master.

### 2. Copy project lên các máy worker
```bash
# Trên máy master
scp -r bigdata/ user@node2-ip:/home/user/
scp -r bigdata/ user@node3-ip:/home/user/
# ... lặp lại cho các node khác
```

### 3. Trên mỗi máy worker
- [ ] Đã có file .env với IP đúng
- [ ] Docker và Docker Compose đã cài
- [ ] Có thể ping giữa các máy

## 🚀 THỨ TỰ KHỞI ĐỘNG

### Bước 1: Node 2 (Kafka) - CHẠY ĐẦU TIÊN
```bash
cd bigdata
./start-node.sh 2
# Hoặc: docker-compose --profile node2 up -d
```

**Đợi 30 giây**, sau đó kiểm tra:
```bash
docker logs parking-kafka | tail -10
docker logs parking-camera-producer | tail -10
```

### Bước 2: Node 5 (Redis)
```bash
cd bigdata
./start-node.sh 5
```

**Kiểm tra:**
```bash
docker exec -it parking-redis-cache redis-cli -n 2 PING
# Phải trả về: PONG
```

### Bước 3: Node 4 (Cassandra)
```bash
cd bigdata
./start-node.sh 4
```

**Đợi 60 giây**, sau đó tạo schema:
```bash
docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/create-tables.cql
```

### Bước 4: Node 3 (Spark)
```bash
cd bigdata
./start-node.sh 3
```

**Đợi 30 giây**, kiểm tra logs:
```bash
docker logs parking-spark-master | tail -30
# Phải thấy: "Spark Streaming started!"
```

### Bước 5: Node 6 (Dashboard)
```bash
cd bigdata
./start-node.sh 6
```

**Truy cập**: `http://NODE6_IP:8501`

### Bước 6: Node 1 (Airflow) - Optional
```bash
cd bigdata
./start-node.sh 1
```

**Truy cập**: `http://NODE1_IP:8080` (airflow/airflow)

## 🔍 Kiểm tra Sau khi Khởi động

### 1. Producer đang gửi events?
```bash
docker logs -f parking-camera-producer
# Phải thấy: "✅ Event #X sent: ..."
```

### 2. Spark đang xử lý?
```bash
docker logs -f parking-spark-master
# Phải thấy: "📦 Processing batch #X"
# Phải thấy: "✅ Redis cache updated"
```

### 3. Redis có data?
```bash
docker exec -it parking-redis-cache redis-cli -n 2
> KEYS parking:*
> GET parking:occupied_count
```

### 4. Dashboard hiển thị?
- Mở: `http://NODE6_IP:8501`
- Phải thấy: Tổng số vị trí, số vị trí có xe/trống
- Phải thấy: Bảng chi tiết các vị trí

## 🐛 Nếu Có Lỗi

1. **Kiểm tra .env**: IP có đúng không?
2. **Kiểm tra logs**: `docker logs <container-name>`
3. **Kiểm tra network**: Có thể ping giữa các máy không?
4. **Kiểm tra ports**: Có service nào đang chiếm port không?
5. **Xem TESTING_GUIDE.md**: Có section Debug Commands

## ✅ SẴN SÀNG!

Nếu đã hoàn thành checklist trên, hệ thống **SẴN SÀNG** để test!

**Chúc bạn test thành công!** 🎉

---

**Lưu ý cuối**: Nếu test trên cùng 1 máy (localhost), sửa IP thành `localhost` hoặc `127.0.0.1` trong .env, nhưng sẽ không phản ánh kiến trúc phân tán.

