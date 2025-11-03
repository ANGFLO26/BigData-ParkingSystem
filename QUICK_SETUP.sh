#!/bin/bash

# Script tự động setup .env cho từng node
# Usage: ./QUICK_SETUP.sh <node_number>
# Example: ./QUICK_SETUP.sh 2

NODE_NUM=$1

if [ -z "$NODE_NUM" ]; then
    echo "Usage: ./QUICK_SETUP.sh <node_number>"
    echo "  node_number: 1, 2, 3, 4, 5, or 6"
    echo ""
    echo "Hãy nhập IP của từng node khi được hỏi"
    exit 1
fi

MASTER_IP="192.168.80.84"

echo "🔧 Setup .env cho Node $NODE_NUM"
echo "Máy Master: $MASTER_IP"
echo ""

# Lấy IP của node hiện tại
case $NODE_NUM in
    1)
        CURRENT_NODE_IP="192.168.80.84"
        echo "Node 1 (Airflow) - Máy Master: $CURRENT_NODE_IP"
        ;;
    2)
        read -p "Nhập IP của máy Node 2 (Kafka): " CURRENT_NODE_IP
        ;;
    3)
        read -p "Nhập IP của máy Node 3 (Spark): " CURRENT_NODE_IP
        ;;
    4)
        read -p "Nhập IP của máy Node 4 (Cassandra): " CURRENT_NODE_IP
        ;;
    5)
        read -p "Nhập IP của máy Node 5 (Redis): " CURRENT_NODE_IP
        ;;
    6)
        read -p "Nhập IP của máy Node 6 (Dashboard): " CURRENT_NODE_IP
        ;;
    *)
        echo "❌ Invalid node number. Must be 1-6"
        exit 1
        ;;
esac

# Lấy IP các node khác
echo ""
echo "Nhập IP của các node khác (hoặc Enter để dùng mặc định):"
read -p "Node 2 IP (Kafka) [192.168.80.85]: " NODE2_IP
NODE2_IP=${NODE2_IP:-192.168.80.85}

read -p "Node 3 IP (Spark) [192.168.80.86]: " NODE3_IP
NODE3_IP=${NODE3_IP:-192.168.80.86}

read -p "Node 4 IP (Cassandra) [192.168.80.87]: " NODE4_IP
NODE4_IP=${NODE4_IP:-192.168.80.87}

read -p "Node 5 IP (Redis) [192.168.80.88]: " NODE5_IP
NODE5_IP=${NODE5_IP:-192.168.80.88}

read -p "Node 6 IP (Dashboard) [192.168.80.89]: " NODE6_IP
NODE6_IP=${NODE6_IP:-192.168.80.89}

# Tạo file .env
cat > .env << EOF
MASTER_IP=$MASTER_IP

NODE1_IP=192.168.80.84
NODE2_IP=$NODE2_IP
NODE3_IP=$NODE3_IP
NODE4_IP=$NODE4_IP
NODE5_IP=$NODE5_IP
NODE6_IP=$NODE6_IP

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

KAFKA_BOOTSTRAP_SERVERS=\${NODE2_IP}:9092
REDIS_CACHE_HOST=\${NODE5_IP}
REDIS_CACHE_PORT=\${REDIS_CACHE_PORT}
CASSANDRA_HOST=\${NODE4_IP}
CASSANDRA_PORT=\${CASSANDRA_PORT}
EOF

echo ""
echo "✅ File .env đã được tạo!"
echo ""
echo "📋 Thông tin:"
echo "   Node hiện tại (Node $NODE_NUM): $CURRENT_NODE_IP"
echo "   Node 2 (Kafka): $NODE2_IP"
echo "   Node 3 (Spark): $NODE3_IP"
echo "   Node 4 (Cassandra): $NODE4_IP"
echo "   Node 5 (Redis): $NODE5_IP"
echo "   Node 6 (Dashboard): $NODE6_IP"
echo ""
echo "📝 Kiểm tra file:"
echo "   cat .env | grep NODE"
echo ""
echo "🚀 Chạy node:"
echo "   docker-compose --profile node$NODE_NUM up -d"

