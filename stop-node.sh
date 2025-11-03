#!/bin/bash

# Script để dừng node tương ứng
# Usage: ./stop-node.sh <node_number>

NODE_NUM=$1

if [ -z "$NODE_NUM" ]; then
    echo "Usage: ./stop-node.sh <node_number>"
    echo "  node_number: 1, 2, 3, 4, 5, or 6"
    exit 1
fi

case $NODE_NUM in
    1)
        echo "🛑 Stopping Node 1: Airflow + Redis (Celery)"
        docker-compose --profile node1 down
        ;;
    2)
        echo "🛑 Stopping Node 2: Camera Producer + Kafka"
        docker-compose --profile node2 down
        ;;
    3)
        echo "🛑 Stopping Node 3: Spark Streaming"
        docker-compose --profile node3 down
        ;;
    4)
        echo "🛑 Stopping Node 4: Cassandra"
        docker-compose --profile node4 down
        ;;
    5)
        echo "🛑 Stopping Node 5: Redis Cache"
        docker-compose --profile node5 down
        ;;
    6)
        echo "🛑 Stopping Node 6: Streamlit Dashboard"
        docker-compose --profile node6 down
        ;;
    *)
        echo "❌ Invalid node number. Must be 1-6"
        exit 1
        ;;
esac

echo "✅ Node $NODE_NUM stopped!"

