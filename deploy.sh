#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目名称（从 docker-compose.yaml 中获取容器名）
CONTAINER_NAME="3hua-001-app"
PROJECT_NAME="3hua-001"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 docker-compose 命令
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        print_error "docker-compose 或 docker compose 命令未找到，请先安装 Docker Compose"
        exit 1
    fi
    print_info "使用命令: $DOCKER_COMPOSE_CMD"
}

# 检查容器是否存在
check_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "检测到容器 ${CONTAINER_NAME} 已存在"
        return 0
    else
        print_info "容器 ${CONTAINER_NAME} 不存在"
        return 1
    fi
}

# 停止并删除容器
stop_container() {
    print_info "正在停止并删除现有容器..."
    $DOCKER_COMPOSE_CMD down
    if [ $? -eq 0 ]; then
        print_success "容器已成功停止并删除"
    else
        print_error "停止容器失败"
        exit 1
    fi
}

# 构建和启动容器
deploy() {
    local build_args=""
    
    # 检查是否使用 --no-cache 参数
    if [ "$1" = "--no-cache" ]; then
        build_args="--no-cache"
        print_warning "使用无缓存模式构建镜像"
    else
        print_info "使用缓存模式构建镜像"
    fi
    
    print_info "开始构建并启动容器..."
    
    # 构建并启动
    if [ -n "$build_args" ]; then
        $DOCKER_COMPOSE_CMD up -d --build $build_args
    else
        $DOCKER_COMPOSE_CMD up -d --build
    fi
    
    if [ $? -eq 0 ]; then
        print_success "容器已成功启动"
        
        # 等待容器启动
        print_info "等待容器启动..."
        sleep 3
        
        # 显示容器状态
        print_info "容器状态:"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
    else
        print_error "容器启动失败"
        exit 1
    fi
}

# 显示日志
show_logs() {
    print_info "开始显示容器日志 (按 Ctrl+C 退出)..."
    echo ""
    sleep 1
    $DOCKER_COMPOSE_CMD logs -f
}

# 主流程
main() {
    echo ""
    print_info "=========================================="
    print_info "  ${PROJECT_NAME} 部署脚本"
    print_info "=========================================="
    echo ""

    # 检查 docker-compose
    check_docker_compose

    # 检查容器是否存在
    if check_container; then
        stop_container
        echo ""
    fi

    # 部署
    deploy "$1"
    echo ""

    # 显示日志
    show_logs
}

# 执行主流程
main "$@"
