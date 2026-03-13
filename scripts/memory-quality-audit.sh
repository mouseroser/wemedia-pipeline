#!/bin/bash
# Memory Quality Audit Script
# 检查记忆系统的健康状态

WORKSPACE="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
REPORT_DATE=$(date +%Y%m%d)
REPORT_FILE="$MEMORY_DIR/audit-$REPORT_DATE.md"
REPORT_TS=$(date +"%Y-%m-%d %H:%M:%S")

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 初始化报告
cat > "$REPORT_FILE" <<EOF
# Memory Quality Audit Report

**Date:** $REPORT_TS
**Auditor:** 小光 (memory-quality-audit cron)

---

## 审计项目

EOF

echo "🔍 开始记忆质量审计..."

# 1. 检查 MEMORY.md 是否存在
echo "## 1. MEMORY.md 状态" >> "$REPORT_FILE"
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    MEMORY_SIZE=$(wc -c < "$WORKSPACE/MEMORY.md")
    MEMORY_LINES=$(wc -l < "$WORKSPACE/MEMORY.md")
    echo "✅ **状态:** 存在" >> "$REPORT_FILE"
    echo "- **大小:** $MEMORY_SIZE bytes" >> "$REPORT_FILE"
    echo "- **行数:** $MEMORY_LINES lines" >> "$REPORT_FILE"
    
    # 检查是否过大
    if [ $MEMORY_SIZE -gt 100000 ]; then
        echo "⚠️ **警告:** MEMORY.md 过大 (>100KB)，建议归档旧内容" >> "$REPORT_FILE"
        echo -e "${YELLOW}⚠️  MEMORY.md 过大${NC}"
    fi
else
    echo "❌ **状态:** 不存在" >> "$REPORT_FILE"
    echo -e "${RED}❌ MEMORY.md 不存在${NC}"
fi
echo "" >> "$REPORT_FILE"

# 2. 检查每日记忆文件
echo "## 2. 每日记忆文件" >> "$REPORT_FILE"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

if [ -f "$MEMORY_DIR/$TODAY.md" ]; then
    echo "✅ **今日记忆:** 存在 ($TODAY.md)" >> "$REPORT_FILE"
else
    echo "⚠️ **今日记忆:** 不存在 ($TODAY.md)" >> "$REPORT_FILE"
    echo -e "${YELLOW}⚠️  今日记忆文件不存在${NC}"
fi

if [ -f "$MEMORY_DIR/$YESTERDAY.md" ]; then
    echo "✅ **昨日记忆:** 存在 ($YESTERDAY.md)" >> "$REPORT_FILE"
else
    echo "⚠️ **昨日记忆:** 不存在 ($YESTERDAY.md)" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 3. 检查 shared-context 目录
echo "## 3. Shared Context 状态" >> "$REPORT_FILE"
SHARED_DIR="$WORKSPACE/shared-context"
if [ -d "$SHARED_DIR" ]; then
    echo "✅ **目录:** 存在" >> "$REPORT_FILE"
    echo "- **文件列表:**" >> "$REPORT_FILE"
    ls -1 "$SHARED_DIR" | while read file; do
        echo "  - $file" >> "$REPORT_FILE"
    done
    
    # 检查关键文件
    for key_file in THESIS.md FEEDBACK-LOG.md SIGNALS.md; do
        if [ ! -f "$SHARED_DIR/$key_file" ]; then
            echo "⚠️ **警告:** 缺少关键文件 $key_file" >> "$REPORT_FILE"
            echo -e "${YELLOW}⚠️  缺少 $key_file${NC}"
        fi
    done
else
    echo "❌ **目录:** 不存在" >> "$REPORT_FILE"
    echo -e "${RED}❌ shared-context 目录不存在${NC}"
fi
echo "" >> "$REPORT_FILE"

# 4. 检查 intel 目录
echo "## 4. Intel 协作文件" >> "$REPORT_FILE"
INTEL_DIR="$WORKSPACE/intel"
if [ -d "$INTEL_DIR" ]; then
    echo "✅ **目录:** 存在" >> "$REPORT_FILE"
    FILE_COUNT=$(ls -1 "$INTEL_DIR" 2>/dev/null | wc -l)
    echo "- **文件数量:** $FILE_COUNT" >> "$REPORT_FILE"
    
    if [ $FILE_COUNT -eq 0 ]; then
        echo "⚠️ **提示:** intel 目录为空" >> "$REPORT_FILE"
    fi
else
    echo "⚠️ **目录:** 不存在" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 5. 统计记忆文件数量
echo "## 5. 记忆文件统计" >> "$REPORT_FILE"
if [ -d "$MEMORY_DIR" ]; then
    TOTAL_FILES=$(ls -1 "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
    echo "- **总文件数:** $TOTAL_FILES" >> "$REPORT_FILE"
    
    # 最近7天的文件
    RECENT_COUNT=0
    for i in {0..6}; do
        CHECK_DATE=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "$i days ago" +%Y-%m-%d)
        if [ -f "$MEMORY_DIR/$CHECK_DATE.md" ]; then
            RECENT_COUNT=$((RECENT_COUNT + 1))
        fi
    done
    echo "- **最近7天文件数:** $RECENT_COUNT / 7" >> "$REPORT_FILE"
    
    if [ $RECENT_COUNT -lt 5 ]; then
        echo "⚠️ **警告:** 最近7天记忆文件不完整" >> "$REPORT_FILE"
        echo -e "${YELLOW}⚠️  最近7天记忆文件不完整 ($RECENT_COUNT/7)${NC}"
    fi
else
    echo "❌ **memory 目录不存在**" >> "$REPORT_FILE"
    echo -e "${RED}❌ memory 目录不存在${NC}"
fi
echo "" >> "$REPORT_FILE"

# 6. 总结
echo "## 审计总结" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "审计完成时间: $(date +"%Y-%m-%d %H:%M:%S")" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "*此报告由 memory-quality-audit cron 自动生成*" >> "$REPORT_FILE"

echo "✅ 审计报告已生成: $REPORT_FILE"

# 检查是否有告警（通过检查报告中的 ❌ 和 ⚠️）
if grep -q "❌" "$REPORT_FILE" || grep -q "⚠️" "$REPORT_FILE"; then
    echo ""
    echo -e "${YELLOW}⚠️  发现告警，需要推送通知${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ 所有检查通过${NC}"
    exit 0
fi
