"""
Airflow DAG để điều phối và giám sát hệ thống đỗ xe
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'parking-admin',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'parking_system_monitor',
    default_args=default_args,
    description='Monitor và điều phối hệ thống đỗ xe',
    schedule_interval=timedelta(minutes=5),  # Chạy mỗi 5 phút
    start_date=days_ago(1),
    catchup=False,
    tags=['parking', 'monitoring'],
)

# Task 1: Health check Kafka
check_kafka = BashOperator(
    task_id='check_kafka_health',
    bash_command='echo "Checking Kafka health..." && nc -z ${KAFKA_HOST:-192.168.1.11} ${KAFKA_PORT:-9092} && echo "Kafka is healthy" || echo "Kafka is down"',
    dag=dag,
)

# Task 2: Health check Redis
check_redis = BashOperator(
    task_id='check_redis_health',
    bash_command='echo "Checking Redis health..." && nc -z ${REDIS_HOST:-192.168.1.14} ${REDIS_PORT:-6379} && echo "Redis is healthy" || echo "Redis is down"',
    dag=dag,
)

# Task 3: Health check Cassandra
check_cassandra = BashOperator(
    task_id='check_cassandra_health',
    bash_command='echo "Checking Cassandra health..." && nc -z ${CASSANDRA_HOST:-192.168.1.13} ${CASSANDRA_PORT:-9042} && echo "Cassandra is healthy" || echo "Cassandra is down"',
    dag=dag,
)

# Task 4: Health check Spark
check_spark = BashOperator(
    task_id='check_spark_health',
    bash_command='echo "Checking Spark health..." && curl -s http://${SPARK_HOST:-192.168.1.12}:${SPARK_UI_PORT:-8080} > /dev/null && echo "Spark is healthy" || echo "Spark is down"',
    dag=dag,
)

# Task 5: Summary report
def generate_summary(**context):
    """Tạo báo cáo tổng hợp"""
    print("📊 Generating system summary...")
    print(f"Execution date: {context['execution_date']}")
    # Có thể thêm logic để đọc từ Redis/Cassandra và tạo report
    return "Summary generated successfully"

summary_task = PythonOperator(
    task_id='generate_summary',
    python_callable=generate_summary,
    dag=dag,
)

# Task dependencies
[check_kafka, check_redis, check_cassandra, check_spark] >> summary_task

