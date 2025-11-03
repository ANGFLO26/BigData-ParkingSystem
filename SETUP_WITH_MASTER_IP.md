# 🔧 Setup với Máy Master IP: 192.168.80.84

## 📋 Thông tin Máy Master

- **IP Master**: `192.168.80.84`
- Máy master có thể đóng vai trò **Node 1 (Airflow)** hoặc chỉ để quản lý

## 🎯 Các Tùy chọn Setup

### Option 1: Chạy Node 1 (Airflow) trên Máy Master

Nếu bạn muốn chạy Airflow trên máy master:

```bash
# Trên máy master (192.168.80.84)
cd bigdata
cp .env.template .env
nano .env  # Sửa NODE1_IP=192.168.80.84
```

File `.env` sẽ như sau:
```env
NODE1_IP=192.168.80.84  # Máy master
NODE2_IP=192.168.80.85  # Máy Node 2 (Kafka)
NODE3_IP=192.168.80.86  # Máy Node 3 (Spark)
NODE4_IP=192.168.80.87  # Máy Node 4 (Cassandra)
NODE5_IP=192.168.80.88  # Máy Node 5 (Redis)
NODE6_IP=192.168.80.89  # Máy Node 6 (Dashboard)
```

### Option 2: Test Tất cả trên Máy Master (Development)

Nếu bạn muốn test tất cả trên cùng máy master (không phân tán):

```bash
# Trên máy master
cd bigdata
cp .env.template .env
nano .env
```

Sửa tất cả IP thành `192.168.80.84`:
```env
NODE1_IP=192.168.80.84
NODE2_IP=192.168.80.84
NODE3_IP=192.168.80.84
NODE4_IP=192.168.80.84
NODE5_IP=192.168.80.84
NODE6_IP=192.168.80.84

KAFKA_BOOTSTRAP_SERVERS=192.168.80.84:9092
REDIS_CACHE_HOST=192.168.80.84
CASSANDRA_HOST=192.168.80.84
```

**Lưu ý**: Khi chạy trên cùng máy, các ports phải khác nhau để tránh conflict.

## 🚀 Quick Setup Script

Tạo script để tự động setup với IP master:

```bash
# Tạo file .env từ template
cd bigdata
cp .env.template .env

# Nếu muốn test trên cùng máy master:
sed -i 's/NODE[1-6]_IP=.*/NODE1_IP=192.168.80.84\nNODE2_IP=192.168.80.84\nNODE3_IP=192.168.80.84\nNODE4_IP=192.168.80.84\nNODE5_IP=192.168.80.84\nNODE6_IP=192.168.80.84/' .env

# Hoặc nếu phân tán, chỉ cập nhật NODE1:
sed -i 's/^NODE1_IP=.*/NODE1_IP=192.168.80.84/' .env
```

## 📝 Checklist Setup

### 1. Trên Máy Master (192.168.80.84)

```bash
cd bigdata

# Tạo file .env
cp .env.template .env

# Nếu chạy Node 1 trên master:
# Sửa NODE1_IP=192.168.80.84 trong .env

# Chạy Node 1 (nếu chạy trên master)
docker-compose --profile node1 up -d
```

### 2. Trên Các Máy Worker

Copy project và cập nhật `.env`:

```bash
# Từ máy master, copy lên worker:
scp -r bigdata/ user@192.168.80.85:/home/user/
scp -r bigdata/ user@192.168.80.86:/home/user/
# ... cho các node khác

# Trên mỗi máy worker, sửa .env:
# - NODE2_IP: IP của máy đó (ví dụ: 192.168.80.85 cho Node 2)
# - KAFKA_BOOTSTRAP_SERVERS: IP của máy Node 2
# - REDIS_CACHE_HOST: IP của máy Node 5
# - CASSANDRA_HOST: IP của máy Node 4
```

## 🔍 Kiểm tra Network

Đảm bảo các máy có thể giao tiếp:

```bash
# Trên máy master, ping các máy khác:
ping 192.168.80.85  # Node 2
ping 192.168.80.86  # Node 3
# ... cho các node khác
```

## 📊 IP Mapping

| Node | Chức năng | IP (mẫu) | IP Master |
|------|-----------|----------|-----------|
| Node 1 | Airflow | 192.168.80.84 | ✅ |
| Node 2 | Kafka | 192.168.80.85 | - |
| Node 3 | Spark | 192.168.80.86 | - |
| Node 4 | Cassandra | 192.168.80.87 | - |
| Node 5 | Redis | 192.168.80.88 | - |
| Node 6 | Dashboard | 192.168.80.89 | - |

## ✅ Sau khi Setup

1. **Kiểm tra .env trên mỗi máy**:
   ```bash
   cat .env | grep -E "NODE[1-6]_IP|KAFKA_BOOTSTRAP_SERVERS|REDIS_CACHE_HOST|CASSANDRA_HOST"
   ```

2. **Kiểm tra network connectivity**:
   ```bash
   # Từ Node 3, ping Node 2 (Kafka)
   ping 192.168.80.85
   
   # Từ Node 6, ping Node 5 (Redis)
   ping 192.168.80.88
   ```

3. **Chạy theo thứ tự** (xem QUICKSTART.md):
   - Node 2 (Kafka) → Node 5 (Redis) → Node 4 (Cassandra) → Node 3 (Spark) → Node 6 (Dashboard) → Node 1 (Airflow)

## 🎯 Kết luận

Với IP master `192.168.80.84`, bạn có thể:
- ✅ Chạy Node 1 (Airflow) trên máy master
- ✅ Hoặc test tất cả trên máy master (development)
- ✅ Hoặc dùng máy master để quản lý và deploy lên các máy worker

**Tiếp theo**: Xem `QUICKSTART.md` hoặc `TESTING_GUIDE.md` để bắt đầu test!

