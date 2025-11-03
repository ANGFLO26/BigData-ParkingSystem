"""
Streamlit Dashboard - Realtime Parking System Monitor
Node 6: Hiển thị trạng thái bãi đỗ xe realtime
"""
import streamlit as st
import redis
import json
import os
import time
from datetime import datetime
import pandas as pd

# ============================================
# CONFIGURATION
# ============================================
REDIS_HOST = os.getenv("REDIS_CACHE_HOST", "192.168.1.14")
REDIS_PORT = int(os.getenv("REDIS_CACHE_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "2"))

# Streamlit page config
st.set_page_config(
    page_title="Hệ Thống Đỗ Xe Thông Minh",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# REDIS CONNECTION
# ============================================
@st.cache_resource
def get_redis_connection():
    """Tạo Redis connection với caching"""
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
        st.error(f"❌ Không thể kết nối Redis: {e}")
        return None

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_all_parking_locations():
    """Lấy danh sách tất cả các vị trí đỗ xe"""
    return [
        f"{floor}{num}" 
        for floor in ["A", "B", "C", "D", "E", "F"] 
        for num in range(1, 11)
    ]

def get_location_data(redis_conn, location):
    """Lấy dữ liệu của một vị trí từ Redis"""
    key = f"parking:location:{location}"
    data = redis_conn.get(key)
    if data:
        return json.loads(data)
    return None

def format_duration(minutes):
    """Format thời gian đỗ"""
    if minutes < 60:
        return f"{int(minutes)} phút"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours} giờ {mins} phút"

def format_money(amount):
    """Format tiền VNĐ"""
    return f"{int(amount):,} VNĐ"

# ============================================
# MAIN APP
# ============================================
st.title("🚗 Hệ Thống Đỗ Xe Thông Minh")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Cấu hình")
    st.write(f"**Redis:** {REDIS_HOST}:{REDIS_PORT}")
    st.write(f"**Database:** {REDIS_DB}")
    
    auto_refresh = st.checkbox("🔄 Tự động làm mới", value=True)
    refresh_interval = st.slider("⏱️ Khoảng thời gian (giây)", 1, 10, 2)
    
    if st.button("🔄 Làm mới ngay"):
        st.rerun()

# Connect to Redis
redis_conn = get_redis_connection()

if not redis_conn:
    st.error("⚠️ Không thể kết nối đến Redis. Vui lòng kiểm tra kết nối.")
    st.stop()

# Get summary data
try:
    total_locations = int(redis_conn.get("parking:total_locations") or 60)
    occupied_count = int(redis_conn.get("parking:occupied_count") or 0)
    empty_count = int(redis_conn.get("parking:empty_count") or total_locations)
except:
    total_locations = 60
    occupied_count = 0
    empty_count = 60

# ============================================
# SUMMARY CARDS
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Tổng số vị trí", total_locations)

with col2:
    st.metric("✅ Vị trí có xe", occupied_count, delta=None)

with col3:
    st.metric("🅿️ Vị trí trống", empty_count, delta=None)

with col4:
    occupancy_rate = (occupied_count / total_locations * 100) if total_locations > 0 else 0
    st.metric("📈 Tỷ lệ sử dụng", f"{occupancy_rate:.1f}%")

st.markdown("---")

# ============================================
# PARKING GRID
# ============================================
st.header("🗺️ Bản đồ bãi đỗ xe")

# Tạo grid cho từng tầng
all_locations = get_all_parking_locations()
parking_data = []

for location in all_locations:
    data = get_location_data(redis_conn, location)
    if data:
        parking_data.append({
            "Vị trí": location,
            "Biển số": data.get("license_plate", "-"),
            "Trạng thái": "Có xe" if data.get("status") == "occupied" else "Trống",
            "Thời gian đỗ": format_duration(data.get("parking_duration_minutes", 0)),
            "Phí đỗ": format_money(data.get("parking_fee", 0))
        })
    else:
        parking_data.append({
            "Vị trí": location,
            "Biển số": "-",
            "Trạng thái": "Trống",
            "Thời gian đỗ": "-",
            "Phí đỗ": "-"
        })

# Display as DataFrame
df = pd.DataFrame(parking_data)

# Tạo tabs cho từng tầng
tabs = st.tabs(["Tất cả", "Tầng A", "Tầng B", "Tầng C", "Tầng D", "Tầng E", "Tầng F (VIP)"])

# Tab: Tất cả
with tabs[0]:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=600
    )

# Tabs cho từng tầng
for idx, floor in enumerate(["A", "B", "C", "D", "E", "F"], 1):
    with tabs[idx]:
        floor_df = df[df["Vị trí"].str.startswith(floor)]
        st.dataframe(
            floor_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )

st.markdown("---")

# ============================================
# DETAILED VIEW
# ============================================
st.header("📋 Chi tiết các vị trí có xe đỗ")

occupied_data = []
for location in all_locations:
    data = get_location_data(redis_conn, location)
    if data and data.get("status") == "occupied":
        occupied_data.append({
            "Vị trí": location,
            "Biển số": data.get("license_plate", "-"),
            "Thời gian đỗ": format_duration(data.get("parking_duration_minutes", 0)),
            "Phí đỗ": format_money(data.get("parking_fee", 0)),
            "Bắt đầu": datetime.fromtimestamp(data.get("start_time", 0)).strftime("%H:%M:%S") if data.get("start_time") else "-"
        })

if occupied_data:
    occupied_df = pd.DataFrame(occupied_data)
    st.dataframe(
        occupied_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Tổng doanh thu
    total_revenue = sum(
        float(str(row["Phí đỗ"]).replace(",", "").replace(" VNĐ", ""))
        for row in occupied_data
        if "VNĐ" in str(row["Phí đỗ"])
    )
    st.success(f"💰 **Tổng doanh thu hiện tại:** {format_money(total_revenue)}")
else:
    st.info("ℹ️ Hiện tại không có xe nào đang đỗ")

# ============================================
# AUTO REFRESH
# ============================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

