#!/bin/bash

# Script để setup .env với IP máy master: 192.168.80.84

MASTER_IP="192.168.80.84"

echo "🔧 Setting up .env file with Master IP: $MASTER_IP"
echo ""

# Tạo file .env
cat > .env << EOF
# ============================================
# CONFIGURATION FOR DISTRIBUTED PARKING SYSTEM
# ============================================
# Máy Master IP
MASTER_IP=$MASTER_IP

# Node 1: Airflow + Redis (Celery)
# Chạy trên máy master
NODE1_IP=$MASTER_IP
REDIS_CELERY_PORT=6379
AIRFLOW_WEBSERVER_PORT=8080

# Node 2: Camera Producer + Kafka Broker
# CẬP NHẬT IP THỰC CỦA MÁY NODE 2
NODE2_IP=192.168.80.85
KAFKA_BROKER_PORT=9092
KAFKA_ZOOKEEPER_PORT=2181
KAFKA_TOPIC=parking-events

# Node 3: Spark Streaming Processor
# CẬP NHẬT IP THỰC CỦA MÁY NODE 3
NODE3_IP=192.168.80.86
SPARK_MASTER_PORT=7077
SPARK_UI_PORT=4040

# Node 4: Cassandra Database
# CẬP NHẬT IP THỰC CỦA MÁY NODE 4
NODE4_IP=192.168.80.87
CASSANDRA_PORT=9042
CASSANDRA_CQL_PORT=7000

# Node 5: Redis (Realtime Cache)
# CẬP NHẬT IP THỰC CỦA MÁY NODE 5
NODE5_IP=192.168.80.88
REDIS_CACHE_PORT=6379
REDIS_DB=2

# Node 6: Streamlit Dashboard
# CẬP NHẬT IP THỰC CỦA MÁY NODE 6
NODE6_IP=192.168.80.89
DASHBOARD_PORT=8501

# Parking Fee Configuration
PRICE_PER_MINUTE=10000

# Kafka Configuration
# QUAN TRỌNG: Phải là IP thực của Node 2
KAFKA_BOOTSTRAP_SERVERS=\${NODE2_IP}:9092

# Redis Configuration
# QUAN TRỌNG: Phải là IP thực của Node 5
REDIS_CACHE_HOST=\${NODE5_IP}
REDIS_CACHE_PORT=\${REDIS_CACHE_PORT}

# Cassandra Configuration
# QUAN TRỌNG: Phải là IP thực của Node 4
CASSANDRA_HOST=\${NODE4_IP}
CASSANDRA_PORT=\${CASSANDRA_PORT}
EOF

echo "✅ File .env đã được tạo!"
echo ""
echo "📋 Kiểm tra file .env:"
echo "   cat .env"
echo ""
echo "⚠️  QUAN TRỌNG:"
echo "   1. Nếu test trên cùng máy master, sửa tất cả NODE*_IP thành $MASTER_IP"
echo "   2. Nếu phân tán, sửa IP cho đúng với từng máy worker"
echo ""
echo "📝 Để chỉnh sửa:"
echo "   nano .env"
echo ""

