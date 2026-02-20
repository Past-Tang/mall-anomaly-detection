<div align="center">
  <img src="assets/logo.svg" alt="Mall Security Anomaly Detect" width="680"/>

  # Mall Security Anomaly Detect

  **商场视频监控异常行为检测系统**

  [![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-blue?style=flat-square)](https://ultralytics.com)
</div>

---

## 概述

基于 YOLOv8 的商场视频监控异常行为检测系统，支持实时视频流分析，自动识别异常行为并告警。包含用户登录注册系统和 Web 可视化界面。

## 功能特性

- **异常检测** -- 基于 YOLOv8 模型的实时异常行为识别
- **Web 界面** -- Streamlit 构建的可视化监控面板
- **用户系统** -- 登录注册功能，数据持久化存储
- **模型推理** -- 支持自定义训练模型 (best.pt)

## 项目结构

```
商场视频监控异常行为检测系统/
├── main_app.py                # 主应用
├── anomaly_detection_app.py   # 异常检测模块
├── login_register.py          # 用户登录注册
├── best.pt                    # 自定义训练模型
├── yolov8n.pt                 # YOLOv8 基础模型
└── requirements.txt           # 依赖列表
```

## 免责声明

本项目仅供学习研究使用。