#!/bin/bash

# Linux System Monitoring Script
# Compatible with RHEL and Rocky Linux

CSV_FILE="${1:-system_stats.csv}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Create CSV header if file does not exist
if [ ! -f "$CSV_FILE" ]; then
    echo "Timestamp,Metric,Filesystem,Total,Used,Available,Usage_Percent" > "$CSV_FILE"
fi

echo "======================================"
echo "       LINUX SYSTEM MONITOR"
echo "======================================"
echo "Timestamp: $TIMESTAMP"

# Function to write CSV data
write_csv() {
    echo "\"$TIMESTAMP\",$1,$2,$3,$4,$5,$6" >> "$CSV_FILE"
}

# Disk Usage
echo
echo "----- DISK USAGE -----"

df -PT -x tmpfs -x devtmpfs | tail -n +2 |
while read -r filesystem type size used avail percent mount; do

    echo "Filesystem: $filesystem"
    echo "Mount: $mount"
    echo "Total: ${size} KB"
    echo "Used: ${used} KB"
    echo "Available: ${avail} KB"
    echo "Usage: $percent"
    echo "----------------------"

    write_csv "Disk" "\"$mount\"" "$size" "$used" "$avail" "$percent"

done

# RAM Usage
echo
echo "----- RAM USAGE -----"

read -r total used available < <(
    awk '
    /^MemTotal:/ {total=$2}
    /^MemAvailable:/ {available=$2}
    END {
        used=total-available
        print total, used, available
    }' /proc/meminfo
)

ram_percent=$(awk -v u="$used" -v t="$total" \
    'BEGIN {printf "%.2f%%", (u/t)*100}')

echo "Total RAM: $((total / 1024)) MB"
echo "Used RAM: $((used / 1024)) MB"
echo "Available RAM: $((available / 1024)) MB"
echo "RAM Usage: $ram_percent"

write_csv "RAM" "\"Memory\"" "$total" "$used" "$available" "$ram_percent"

# Swap Usage
echo
echo "----- SWAP USAGE -----"

read -r swap_total swap_free < <(
    awk '
    /^SwapTotal:/ {total=$2}
    /^SwapFree:/ {free=$2}
    END {print total, free}
    ' /proc/meminfo
)

swap_used=$((swap_total - swap_free))

if [ "$swap_total" -gt 0 ]; then
    swap_percent=$(awk -v u="$swap_used" -v t="$swap_total" \
        'BEGIN {printf "%.2f%%", (u/t)*100}')
else
    swap_percent="0.00%"
fi

echo "Total Swap: $((swap_total / 1024)) MB"
echo "Used Swap: $((swap_used / 1024)) MB"
echo "Free Swap: $((swap_free / 1024)) MB"
echo "Swap Usage: $swap_percent"

write_csv "Swap" "\"Swap\"" "$swap_total" "$swap_used" "$swap_free" "$swap_percent"

echo
echo "======================================"
echo "Monitoring completed successfully!"
echo "CSV File: $CSV_FILE"
echo "======================================"
