#!/bin/bash

# Script để khởi động node tương ứng
# Usage: ./start-node.sh <node_number>

NODE_NUM=$1

if [ -z "$NODE_NUM" ]; then
    echo "Usage: ./start-node.sh <node_number>"
    echo "  node_number: 1, 2, 3, 4, 5, or 6"
    exit 1
fi

case $NODE_NUM in
    1)
        echo "🚀 Starting Node 1: Airflow + Redis (Celery)"
        docker-compose --profile node1 up -d
        ;;
    2)
        echo "🚀 Starting Node 2: Camera Producer + Kafka"
        docker-compose --profile node2 up -d
        ;;
    3)
        echo "🚀 Starting Node 3: Spark Streaming"
        docker-compose --profile node3 up -d
        ;;
    4)
        echo "🚀 Starting Node 4: Cassandra"
        docker-compose --profile node4 up -d
        echo "⏳ Waiting for Cassandra to start..."
        sleep 30
        echo "📝 Creating schema..."
        docker exec -it parking-cassandra cqlsh -f /docker-entrypoint-initdb.d/schema.cql || echo "⚠️  Please create schema manually"
        ;;
    5)
        echo "🚀 Starting Node 5: Redis Cache"
        docker-compose --profile node5 up -d
        ;;
    6)
        echo "🚀 Starting Node 6: Streamlit Dashboard"
        docker-compose --profile node6 up -d
        ;;
    *)
        echo "❌ Invalid node number. Must be 1-6"
        exit 1
        ;;
esac

echo "✅ Node $NODE_NUM started!"
docker-compose ps

