"""
Spark Structured Streaming để xử lý events từ Kafka
Tính tiền đỗ xe: 1 phút = 10,000 VNĐ (tính chính xác theo phút)
"""
import os
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, current_timestamp, 
    from_unixtime, unix_timestamp, max as spark_max, last
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, TimestampType
)
import redis

# ============================================
# SPARK STREAMING CONFIGURATION
# ============================================

# Environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.1.11:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "parking-events")
REDIS_HOST = os.getenv("REDIS_CACHE_HOST", "192.168.1.14")
REDIS_PORT = int(os.getenv("REDIS_CACHE_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "2"))
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "192.168.1.13")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
PRICE_PER_MINUTE = float(os.getenv("PRICE_PER_MINUTE", "10000"))

print(f"🔧 Configuration:")
print(f"  Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
print(f"  Topic: {KAFKA_TOPIC}")
print(f"  Redis: {REDIS_HOST}:{REDIS_PORT} DB={REDIS_DB}")
print(f"  Cassandra: {CASSANDRA_HOST}:{CASSANDRA_PORT}")
print(f"  Price per minute: {PRICE_PER_MINUTE:,} VNĐ")

# ============================================
# SPARK SESSION
# ============================================
spark = SparkSession.builder \
    .appName("ParkingStreamProcessor") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ============================================
# SCHEMA DEFINITION
# ============================================
parking_event_schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("timestamp_unix", IntegerType(), True),
    StructField("license_plate", StringType(), True),
    StructField("location", StringType(), True),
    StructField("status_code", StringType(), True)
])

# ============================================
# REDIS HELPER FUNCTIONS
# ============================================
def get_redis_connection():
    """Tạo Redis connection"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except Exception as e:
        print(f"❌ Redis connection error: {e}")
        return None

def update_redis_cache(redis_conn, location_data):
    """Cập nhật Redis cache với dữ liệu realtime"""
    if not redis_conn:
        return
    
    try:
        # Cache tổng quan
        redis_conn.set("parking:total_locations", 60, ex=3600)
        redis_conn.set("parking:occupied_count", location_data.get("occupied_count", 0), ex=3600)
        redis_conn.set("parking:empty_count", location_data.get("empty_count", 60), ex=3600)
        
        # Cache từng vị trí
        for location, data in location_data.get("locations", {}).items():
            key = f"parking:location:{location}"
            redis_conn.set(key, json.dumps(data, ensure_ascii=False), ex=3600)
            
        print(f"✅ Redis cache updated: {location_data.get('occupied_count', 0)} occupied")
    except Exception as e:
        print(f"❌ Redis update error: {e}")

def calculate_parking_fee(start_time_unix, current_time_unix):
    """Tính tiền đỗ xe: 1 phút = 10,000 VNĐ (tính chính xác theo phút)"""
    if start_time_unix is None or current_time_unix is None:
        return 0.0, 0.0
    
    duration_seconds = current_time_unix - start_time_unix
    duration_minutes = duration_seconds / 60.0  # Tính chính xác theo phút (có thể có số thập phân)
    fee = duration_minutes * PRICE_PER_MINUTE
    
    return duration_minutes, fee

# ============================================
# STATE TRACKING (In-memory state)
# ============================================
# Track parking state per vehicle
vehicle_state = {}  # {license_plate: {location, start_time_unix, status}}

# ============================================
# PROCESS EACH BATCH
# ============================================
def process_batch(batch_df, batch_id):
    """Xử lý mỗi batch từ Spark Streaming"""
    print(f"\n📦 Processing batch #{batch_id}")
    
    if batch_df.count() == 0:
        return
    
    # Get Redis connection
    redis_conn = get_redis_connection()
    
    # Convert to list for processing
    rows = batch_df.collect()
    
    # Initialize location data
    location_data = {
        "occupied_count": 0,
        "empty_count": 60,
        "locations": {}
    }
    
    current_time_unix = int(datetime.now().timestamp())
    
    # Process each event
    for row in rows:
        license_plate = row["license_plate"]
        location = row["location"]
        status = row["status_code"]
        event_timestamp_unix = row["timestamp_unix"]
        
        # Initialize vehicle state if not exists
        if license_plate not in vehicle_state:
            vehicle_state[license_plate] = {
                "location": None,
                "start_time_unix": None,
                "status": None
            }
        
        vehicle = vehicle_state[license_plate]
        
        # Handle status transitions
        if status == "ENTERING":
            # Xe đang vào - chưa đỗ, chưa tính tiền
            vehicle["status"] = "ENTERING"
            vehicle["location"] = location
        
        elif status == "PARKED":
            # Xe bắt đầu đỗ - lưu thời gian bắt đầu
            if vehicle["status"] != "PARKED":
                vehicle["start_time_unix"] = event_timestamp_unix
                vehicle["status"] = "PARKED"
                vehicle["location"] = location
            
            # Tính tiền theo thời gian đã đỗ (realtime)
            if vehicle["start_time_unix"]:
                duration_minutes, fee = calculate_parking_fee(
                    vehicle["start_time_unix"], 
                    current_time_unix
                )
                
                # Update location data
                location_data["locations"][location] = {
                    "license_plate": license_plate,
                    "status": "occupied",
                    "parking_duration_minutes": round(duration_minutes, 2),
                    "parking_fee": round(fee, 0),
                    "start_time": vehicle["start_time_unix"]
                }
        
        elif status == "EXITING":
            # Xe ra - tính tiền cuối cùng và clear state
            if vehicle["status"] == "PARKED" and vehicle["start_time_unix"]:
                duration_minutes, fee = calculate_parking_fee(
                    vehicle["start_time_unix"],
                    event_timestamp_unix
                )
                
                print(f"  💰 Xe {license_plate} tại {location}: Đỗ {round(duration_minutes, 2)} phút, Phí: {round(fee, 0):,} VNĐ")
                
                # Lưu vào Cassandra (nếu có connection)
                try:
                    from cassandra.cluster import Cluster
                    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
                    session = cluster.connect()
                    session.execute(
                        """
                        INSERT INTO parking_system.parking_history 
                        (timestamp, license_plate, location, status_code, parking_duration_minutes, parking_fee)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            datetime.fromtimestamp(event_timestamp_unix),
                            license_plate,
                            location,
                            "EXITING",
                            round(duration_minutes, 2),
                            round(fee, 0)
                        )
                    )
                    session.shutdown()
                    cluster.shutdown()
                except Exception as e:
                    print(f"  ⚠️  Cassandra save error: {e}")
            
            # Clear vehicle state
            vehicle["status"] = None
            vehicle["start_time_unix"] = None
            vehicle["location"] = None
            
            # Mark location as empty
            if location in location_data["locations"]:
                location_data["locations"][location] = {
                    "license_plate": "-",
                    "status": "empty",
                    "parking_duration_minutes": 0,
                    "parking_fee": 0
                }
        
        elif status == "MOVING":
            # Xe đang di chuyển - giữ nguyên state
            vehicle["status"] = "MOVING"
    
    # Count occupied locations
    occupied_locations = [
        loc for loc, data in location_data["locations"].items() 
        if data.get("status") == "occupied"
    ]
    location_data["occupied_count"] = len(occupied_locations)
    location_data["empty_count"] = 60 - len(occupied_locations)
    
    # Update Redis cache
    update_redis_cache(redis_conn, location_data)
    
    print(f"  ✅ Processed: {len(rows)} events, {location_data['occupied_count']} occupied")

# ============================================
# SPARK STREAMING QUERY
# ============================================
print("\n🚀 Starting Spark Streaming...")

# Đọc từ Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parse JSON từ Kafka
parsed_df = kafka_df.select(
    from_json(col("value").cast("string"), parking_event_schema).alias("data")
).select(
    col("data.timestamp"),
    col("data.timestamp_unix"),
    col("data.license_plate"),
    col("data.location"),
    col("data.status_code")
).filter(
    col("license_plate").isNotNull() & col("location").isNotNull()
)

# Start streaming
query = parsed_df \
    .writeStream \
    .foreachBatch(process_batch) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .start()

print("\n✅ Spark Streaming started!")
print("📊 Waiting for data from Kafka...")

# Wait for termination
query.awaitTermination()
