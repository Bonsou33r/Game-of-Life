#!/bin/bash

# Conway's Game of Life - Docker Runner Script
# This script helps build and run the containerized Game of Life

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        print_info "On Linux: sudo systemctl start docker"
        print_info "On macOS: Start Docker Desktop"
        print_info "On Windows: Start Docker Desktop"
        exit 1
    fi

    # Check Docker version compatibility
    docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null | cut -d'.' -f1-2)
    if [ -n "$docker_version" ]; then
        print_info "Docker version: $docker_version"
    fi

    print_success "Prerequisites check passed!"
}

# Function to setup X11 forwarding
setup_x11() {
    print_info "Setting up X11 forwarding..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if [ -z "$DISPLAY" ]; then
            print_error "DISPLAY environment variable is not set."
            print_info "Try running: export DISPLAY=:0"
            exit 1
        fi

        # Check if xhost is available
        if ! command_exists xhost; then
            print_error "xhost command not found. Please install x11-xserver-utils."
            print_info "Ubuntu/Debian: sudo apt-get install x11-xserver-utils"
            print_info "RHEL/CentOS: sudo yum install xorg-x11-server-utils"
            exit 1
        fi

        # Allow Docker to connect to X server
        if ! xhost +local:docker >/dev/null 2>&1; then
            print_warning "Could not configure X11 access for Docker."
            print_info "Trying alternative: xhost +local:root"
            xhost +local:root >/dev/null 2>&1 || {
                print_error "Failed to configure X11 access. GUI may not work."
                print_info "Manual fix: xhost +local:docker"
            }
        fi

        print_success "X11 forwarding configured for Linux"

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command_exists xhost; then
            print_error "XQuartz is required for GUI support on macOS."
            print_info "Install with: brew install --cask xquartz"
            print_info "Then restart and run: xhost +localhost"
            exit 1
        fi

        if [ -z "$DISPLAY" ]; then
            export DISPLAY=host.docker.internal:0
            print_info "Set DISPLAY to host.docker.internal:0 for macOS"
        fi

        # Check if XQuartz is running
        if ! pgrep -x "Xquartz" > /dev/null 2>&1; then
            print_warning "XQuartz doesn't appear to be running."
            print_info "Please start XQuartz and ensure 'Allow connections from network clients' is enabled."
        fi

        xhost +localhost >/dev/null 2>&1 || {
            print_warning "Could not configure xhost. Make sure XQuartz is running and configured properly."
            print_info "In XQuartz preferences, enable 'Allow connections from network clients'"
        }

        print_success "X11 forwarding configured for macOS"

    else
        print_warning "OS not automatically detected. Manual X11 setup may be required."
        print_info "Make sure DISPLAY is set and X server allows connections."
    fi
}

# Function to build the Docker image
build_image() {
    print_info "Building Docker image..."
    if ! docker-compose build; then
        print_error "Docker build failed!"
        print_info "Check the error messages above for details."
        print_info "Common issues:"
        print_info "  - Missing files (ensure game files are present)"
        print_info "  - Network connectivity issues"
        print_info "  - Insufficient disk space"
        exit 1
    fi
    print_success "Docker image built successfully!"
}

# Function to run with full interface
run_full() {
    print_info "Starting Game of Life with terminal interface..."
    if ! docker-compose up; then
        print_error "Failed to start the application!"
        print_info "Check the error messages above for details."
        print_info "Try running: $0 clean && $0 build"
        exit 1
    fi
}

# Function to run game only
run_simple() {
    print_info "Starting Game of Life (simple mode)..."
    if ! docker-compose --profile simple up game-only; then
        print_error "Failed to start the application in simple mode!"
        print_info "Check the error messages above for details."
        exit 1
    fi
}

# Function to run in detached mode
run_detached() {
    print_info "Starting Game of Life in background..."
    if ! docker-compose up -d; then
        print_error "Failed to start the application in background!"
        exit 1
    fi
    print_success "Game of Life is running in background."
    print_info "Use '$0 logs' to view logs."
    print_info "Use '$0 stop' to stop."

    # Wait a moment and check if containers are actually running
    sleep 3
    if docker-compose ps | grep -q "Up"; then
        print_success "Container is running successfully."
    else
        print_warning "Container may have stopped. Check logs with '$0 logs'"
    fi
}

# Function to run game directly without launcher
run_direct() {
    print_info "Starting Game of Life directly (no launcher interface)..."
    if ! docker-compose run --rm -it game-of-life python game_of_life_pygame.py; then
        print_error "Failed to start the game directly!"
        print_info "Check the error messages above for details."
        print_info "Try running: $0 clean && $0 build"
        exit 1
    fi
}

# Function to clean up
cleanup() {
    print_info "Cleaning up Docker containers and images..."
    docker-compose down --volumes --remove-orphans
    docker image prune -f
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    cat << EOF
Conway's Game of Life - Docker Runner

Usage: $0 [COMMAND]

Commands:
    build       Build the Docker image
    run         Run with full terminal interface (default)
    simple      Run game only (no terminal interface)
    direct      Run game directly (bypass launcher completely)
    detached    Run in background (detached mode)
    stop        Stop running containers
    clean       Clean up containers and images
    logs        Show container logs
    shell       Open shell in container
    test        Test X11 forwarding
    help        Show this help message

Examples:
    $0              # Run with full interface
    $0 build        # Build the image
    $0 simple       # Run simple version
    $0 direct       # Run game directly (no launcher)
    $0 clean        # Clean up everything

Prerequisites:
    - Docker and Docker Compose
    - X11 forwarding support (Linux/macOS)
    - For macOS: XQuartz installed
    - For Linux: x11-xserver-utils package

EOF
}

# Function to test X11 forwarding
test_x11() {
    print_info "Testing X11 forwarding with xeyes..."
    print_info "This will show xeyes for 10 seconds if X11 is working..."

    if docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        alpine:latest sh -c "apk add --no-cache xeyes > /dev/null 2>&1 && timeout 10 xeyes" 2>/dev/null; then
        print_success "X11 forwarding test passed!"
    else
        print_error "X11 forwarding test failed!"
        print_info "Troubleshooting steps:"
        print_info "1. Check DISPLAY variable: echo \$DISPLAY"
        print_info "2. On Linux: xhost +local:docker"
        print_info "3. On macOS: Make sure XQuartz is running with network clients enabled"
        print_info "4. On Windows: Make sure X server (VcXsrv/Xming) is running"

        # Additional diagnostic info
        print_info "Current DISPLAY: ${DISPLAY:-'not set'}"
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            print_info "X11 socket exists: $([ -S /tmp/.X11-unix/X0 ] && echo 'yes' || echo 'no')"
        fi

        exit 1
    fi
}

# Function to show logs
show_logs() {
    print_info "Showing container logs..."
    docker-compose logs -f
}

# Function to open shell in container
open_shell() {
    print_info "Opening shell in container..."
    docker-compose exec game-of-life bash || {
        print_info "Container not running. Starting a new one..."
        docker-compose run --rm game-of-life bash
    }
}

# Function to stop containers
stop_containers() {
    print_info "Stopping containers..."
    if docker-compose down; then
        print_success "Containers stopped!"
    else
        print_warning "Some containers may not have stopped cleanly."
        print_info "Force stopping with: docker-compose kill"
        docker-compose kill 2>/dev/null || true
    fi
}

# Main script logic
main() {
    echo "Conway's Game of Life - Docker Edition"
    echo "======================================"
    echo

    # Parse command line arguments
    case "${1:-run}" in
        build)
            check_prerequisites
            build_image
            ;;
        run)
            check_prerequisites
            setup_x11
            build_image
            run_full
            ;;
        simple)
            check_prerequisites
            setup_x11
            build_image
            run_simple
            ;;
        direct)
            check_prerequisites
            setup_x11
            build_image
            run_direct
            ;;
        detached|daemon)
            check_prerequisites
            setup_x11
            build_image
            run_detached
            ;;
        stop)
            stop_containers
            ;;
        clean|cleanup)
            cleanup
            ;;
        logs)
            show_logs
            ;;
        shell|bash)
            open_shell
            ;;
        test|test-x11)
            setup_x11
            test_x11
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Trap SIGINT and SIGTERM to clean up properly
cleanup_on_exit() {
    print_info "Shutting down..."
    docker-compose down 2>/dev/null || true
    # Reset X11 permissions if we modified them
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command_exists xhost; then
        xhost -local:docker 2>/dev/null || true
    fi
    exit 0
}
trap cleanup_on_exit INT TERM

# Run main function with all arguments
main "$@"
