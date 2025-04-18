#!/bin/bash
# Скрипт для установки системных зависимостей

echo "Установка системных зависимостей для GraphExtractor..."

# Определяем дистрибутив Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Невозможно определить дистрибутив Linux"
    exit 1
fi

# Устанавливаем зависимости в зависимости от дистрибутива
case $OS in
    "ubuntu"|"debian")
        echo "Обнаружена система Ubuntu/Debian"
        sudo apt-get update
        sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 libgtk-3-0
        ;;
    "fedora"|"rhel"|"centos")
        echo "Обнаружена система Fedora/RHEL/CentOS"
        sudo dnf install -y mesa-libGL mesa-libGLU gtk3 libXext libSM libXrender
        ;;
    "alpine")
        echo "Обнаружена система Alpine Linux"
        apk add --no-cache mesa-gl mesa-glu gtk+3.0 libsm libice libxext libxrender
        ;;
    *)
        echo "Неизвестный дистрибутив: $OS"
        echo "Пожалуйста, установите зависимости вручную:"
        echo "- libGL (OpenGL)"
        echo "- libGLU"
        echo "- GTK-3"
        echo "- X11 библиотеки"
        exit 1
        ;;
esac

echo "Системные зависимости установлены успешно!"
echo "Теперь вы можете запустить тесты командой: python run_all_tests.py"
