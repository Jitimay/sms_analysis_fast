#!/bin/bash

# ProofOfFace Health Check Script
# Verifies all services are running correctly

set -e

echo "🏥 ProofOfFace Health Check"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Function to check port availability
check_port() {
    local service_name=$1
    local port=$2
    
    echo -n "Checking $service_name port $port... "
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓ Open${NC}"
        return 0
    else
        echo -e "${RED}✗ Closed${NC}"
        return 1
    fi
}

# Initialize counters
total_checks=0
passed_checks=0

# Check Substrate Node
echo -e "\n${YELLOW}🔗 Substrate Node${NC}"
total_checks=$((total_checks + 2))

if check_port "Substrate WebSocket" 9944; then
    passed_checks=$((passed_checks + 1))
fi

if check_service "Substrate RPC" "http://localhost:9933/health"; then
    passed_checks=$((passed_checks + 1))
fi

# Check AI Service
echo -e "\n${YELLOW}🤖 AI Service${NC}"
total_checks=$((total_checks + 1))

if check_service "AI Service" "http://localhost:5000/health"; then
    passed_checks=$((passed_checks + 1))
fi

# Check Frontend
echo -e "\n${YELLOW}🎨 Frontend${NC}"
total_checks=$((total_checks + 1))

if check_service "Frontend" "http://localhost:3000" "200\|301\|302"; then
    passed_checks=$((passed_checks + 1))
fi

# Check IPFS (optional)
echo -e "\n${YELLOW}📁 IPFS Node${NC}"
total_checks=$((total_checks + 2))

if check_port "IPFS API" 5001; then
    passed_checks=$((passed_checks + 1))
fi

if check_service "IPFS Gateway" "http://localhost:8080/ipfs/QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn" "200\|404"; then
    passed_checks=$((passed_checks + 1))
fi

# Check PostgreSQL (optional)
echo -e "\n${YELLOW}🗄️  PostgreSQL${NC}"
total_checks=$((total_checks + 1))

if check_port "PostgreSQL" 5432; then
    passed_checks=$((passed_checks + 1))
fi

# Summary
echo -e "\n${YELLOW}📊 Health Check Summary${NC}"
echo "======================="
echo "Passed: $passed_checks/$total_checks"

if [ "$passed_checks" -eq "$total_checks" ]; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    exit 0
elif [ "$passed_checks" -gt $((total_checks / 2)) ]; then
    echo -e "${YELLOW}⚠️  Some services need attention${NC}"
    exit 1
else
    echo -e "${RED}❌ Multiple services are down${NC}"
    exit 2
fi