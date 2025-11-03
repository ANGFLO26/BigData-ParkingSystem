# 🧪 Hướng Dẫn Test Hệ Thống

## 📋 Trước khi Test

### 1. Chuẩn bị môi trường
```bash
# Trên mỗi máy, kiểm tra:
docker --version        # >= 20.10
docker-compose --version # >= 2.0
```

### 2. Tạo file .env
Trên máy master, tạo file `.env`:
```bash
cd bigdata
nano .env
```

Nội dung:
```env
NODE1_IP=192.168.1.10
NODE2_IP=192.168.1.11
NODE3_IP=192.168.1.12
NODE4_IP=192.168.1.13
NODE5_IP=192.168.1.14
NODE6_IP=192.168.1.15

KAFKA_BOOTSTRAP_SERVERS=${NODE2_IP}:9092
REDIS_CACHE_HOST=${NODE5_IP}
REDIS_CACHE_PORT=6379
REDIS_DB=2
CASSANDRA_HOST=${NODE4_IP}
CASSANDRA_PORT=9042
PRICE_PER_MINUTE=10000
KAFKA_TOPIC=parking-events
```

**QUAN TRỌNG**: Sửa IP addresses cho đúng với từng máy!

## 🚀 Bước Test

### Test 1: Node 2 (Kafka + Producer) - Bước đầu tiên

```bash
# Trên Node 2
cd bigdata
docker-compose --profile node2 up -d

# Đợi 30 giây để Kafka khởi động
sleep 30

# Kiểm tra containers
docker ps | grep parking

# Kiểm tra Kafka logs
docker logs parking-kafka | tail -20

# Kiểm tra Producer logs (phải thấy events đang gửi)
docker logs parking-camera-producer | tail -20

# Test consume từ Kafka
docker exec -it parking-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic parking-events \
  --from-beginning \
  --max-messages 5
```

**Kỳ vọng**: Thấy JSON events với license_plate, location, status_code

### Test 2: Node 5 (Redis Cache)

```bash
# Trên Node 5
cd bigdata
docker-compose --profile node5 up -d

# Kiểm tra Redis
docker exec -it parking-redis-cache redis-cli -n 2 PING
# Phải trả về: PONG

# Kiểm tra port
docker port parking-redis-cache
# Phải thấy: 6379/tcp
```

**Kỳ vọng**: Redis đang chạy và có thể connect

### Test 3: Node 4 (Cassandra)

```bash
# Trên Node 4
cd bigdata
docker-compose --profile node4 up -d

# Đợi Cassandra khởi động (30-60 giây)
sleep 60

# Kiểm tra status
docker exec parking-cassandra nodetool status
# Phải thấy: UN (Up Normal)

# Tạo schema
docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/create-tables.cql

# Hoặc thủ công:
docker exec -it parking-cassandra cqlsh
# Trong cqlsh:
DESCRIBE KEYSPACE parking_system;
# Phải thấy keyspace và table parking_history
```

**Kỳ vọng**: Cassandra đang chạy, schema đã được tạo

### Test 4: Node 3 (Spark Streaming)

```bash
# Trên Node 3
cd bigdata

# Kiểm tra .env có đúng IP không
cat .env | grep KAFKA_BOOTSTRAP_SERVERS
# Phải là: KAFKA_BOOTSTRAP_SERVERS=192.168.1.11:9092 (IP Node 2)

cat .env | grep REDIS_CACHE_HOST
# Phải là: REDIS_CACHE_HOST=192.168.1.14 (IP Node 5)

# Start Spark
docker-compose --profile node3 up -d

# Xem logs (đợi 30 giây)
sleep 30
docker logs parking-spark-master | tail -30

# Kiểm tra config
docker logs parking-spark-master | grep "Configuration"
# Phải thấy đúng IP của Kafka, Redis, Cassandra

# Kiểm tra Spark đang xử lý
docker logs parking-spark-master | grep "Processing batch"
# Phải thấy: "📦 Processing batch #X"
```

**Kỳ vọng**: 
- Spark đã connect được Kafka
- Spark đang nhận và xử lý events
- Spark đang update Redis

### Test 5: Node 6 (Dashboard)

```bash
# Trên Node 6
cd bigdata

# Kiểm tra .env
cat .env | grep REDIS_CACHE_HOST
# Phải là IP Node 5

# Start Dashboard
docker-compose --profile node6 up -d

# Đợi 10 giây
sleep 10

# Kiểm tra logs
docker logs parking-dashboard | tail -20

# Truy cập: http://NODE6_IP:8501
```

**Kỳ vọng**: 
- Dashboard mở được
- Hiển thị tổng số vị trí (60)
- Hiển thị số vị trí có xe / trống
- Có bảng chi tiết các vị trí

### Test 6: Node 1 (Airflow) - Optional

```bash
# Trên Node 1
cd bigdata
docker-compose --profile node1 up -d

# Đợi 2 phút để Airflow khởi động
sleep 120

# Truy cập: http://NODE1_IP:8080
# Username/Password: airflow/airflow
```

**Kỳ vọng**: Airflow UI hiển thị, có DAG `parking_system_monitor`

## 🔍 Test End-to-End

### Test tính tiền đỗ xe

1. **Theo dõi một xe cụ thể:**
   - Xem Producer logs để tìm một license_plate
   - Đợi xe đó chuyển sang PARKED
   - Xem Dashboard, tìm vị trí đó
   - Kiểm tra thời gian đỗ và phí tăng dần realtime

2. **Test khi xe ra:**
   - Đợi xe chuyển sang EXITING
   - Kiểm tra Spark logs: Phải thấy "💰 Xe ... tại ...: Đỗ ... phút, Phí: ..."
   - Kiểm tra Cassandra:
     ```bash
     docker exec -it parking-cassandra cqlsh
     SELECT * FROM parking_system.parking_history LIMIT 5;
     ```
   - Kiểm tra Dashboard: Vị trí đó phải thành trống

3. **Kiểm tra tính tiền đúng:**
   - Ví dụ: Xe đỗ 15 phút 30 giây = 15.5 phút
   - Phí phải là: 15.5 * 10000 = 155,000 VNĐ
   - Kiểm tra trong Dashboard và Cassandra

## 🐛 Debug Commands

### Nếu Producer không gửi được:
```bash
docker logs -f parking-camera-producer
# Tìm lỗi kết nối Kafka
```

### Nếu Spark không nhận được data:
```bash
# Kiểm tra Kafka connection
docker exec parking-spark-master ping <NODE2_IP>

# Kiểm tra Kafka có messages không
docker exec -it parking-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic parking-events \
  --from-beginning \
  --max-messages 1

# Xem Spark logs
docker logs -f parking-spark-master
```

### Nếu Redis không có data:
```bash
# Kiểm tra Redis connection từ Spark
docker exec parking-spark-master ping <NODE5_IP>

# Kiểm tra Redis có keys không
docker exec -it parking-redis-cache redis-cli -n 2
> KEYS parking:*
> GET parking:occupied_count

# Xem Spark logs
docker logs parking-spark-master | grep "Redis"
```

### Nếu Dashboard trống:
```bash
# Kiểm tra Redis có data
docker exec -it parking-redis-cache redis-cli -n 2 KEYS parking:*

# Kiểm tra Dashboard logs
docker logs parking-dashboard

# Test Redis connection từ Dashboard
docker exec parking-dashboard ping <NODE5_IP>
```

## ✅ Checklist Test

- [ ] Node 2: Kafka đang chạy, Producer đang gửi events
- [ ] Node 5: Redis đang chạy, có thể connect
- [ ] Node 4: Cassandra đang chạy, schema đã tạo
- [ ] Node 3: Spark đang xử lý events, update Redis
- [ ] Node 6: Dashboard hiển thị dữ liệu
- [ ] Tính tiền đúng: 1 phút = 10,000 VNĐ
- [ ] Realtime updates: Thời gian và phí tăng dần
- [ ] Khi xe ra: Lưu vào Cassandra, Dashboard cập nhật

## 🎯 Kết quả mong đợi

Sau khi test thành công:
1. ✅ Producer gửi events lên Kafka liên tục
2. ✅ Spark nhận và xử lý events
3. ✅ Dashboard hiển thị trạng thái realtime
4. ✅ Tính tiền chính xác theo phút
5. ✅ Lưu lịch sử vào Cassandra khi xe ra

---

**Lưu ý**: Nếu có lỗi, xem logs của service tương ứng và kiểm tra lại .env file có IP đúng không.

