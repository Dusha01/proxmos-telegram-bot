from __future__ import annotations

SAMPLE_CPU_CSV = """,result,table,_start,_stop,_time,_value,_field,_measurement,host,object
,_result,0,2026-11-05T10:00:00Z,2026-11-05T11:00:00Z,2026-11-05T10:05:00Z,1.5,cpu,cpustat,dusha,nodes
,_result,0,2026-11-05T10:00:00Z,2026-11-05T11:00:00Z,2026-11-05T10:10:00Z,2.0,cpu,cpustat,dusha,nodes
"""

SAMPLE_CPU_LAST = """,result,table,_start,_stop,_time,_value,_field,_measurement,host,object
,_result,0,2026-11-05T10:50:00Z,2026-11-05T11:00:00Z,2026-11-05T11:00:00Z,0.02,cpu,cpustat,dusha,nodes
"""

SAMPLE_MEMORY_LAST = """,result,table,_start,_stop,_time,_value,_field,_measurement,host,object
,_result,0,2026-11-05T10:50:00Z,2026-11-05T11:00:00Z,2026-11-05T11:00:00Z,8000000000,memused,memory,dusha,nodes
"""

_SMART_DISK_TEMP_HEADER = ",result,table,_start,_stop,_time,_value,_field,_measurement,device,host"
SAMPLE_SMART_DISK_TEMP_CSV = (
    _SMART_DISK_TEMP_HEADER
    + """
,_result,0,2026-11-05T10:00:00Z,2026-11-05T11:00:00Z,2026-11-05T10:05:00Z,35,temp_c,smart_device,nvme0,dusha
,_result,0,2026-11-05T10:00:00Z,2026-11-05T11:00:00Z,2026-11-05T10:10:00Z,36,temp_c,smart_device,nvme0,dusha
,_result,1,2026-11-05T10:00:00Z,2026-11-05T11:00:00Z,2026-11-05T10:05:00Z,37,temp_c,smart_device,nvme1,dusha
,_result,2,2026-11-05T10:00:00Z,2026-11-05T11:00:00Z,2026-11-05T10:05:00Z,31,temp_c,smart_device,sdb,dusha
"""
)
