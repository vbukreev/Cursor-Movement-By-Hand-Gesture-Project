# AeroPoint Gesture-Driven Cursor Control System

## Team

| Name | Email | Role |
|------|-------|------|
| Preksha Sharda | psharda3@myseneca.ca | Team Member |
| Kunal | k63@myseneca.ca | Team Member |
| Aditi | aditi2@myseneca.ca | Team Member |
| Victoria Bukreev | vbukreev@myseneca.ca  | Team Member |

## Introduction

This repository contains the Capstone II implementation work for **AeroPoint**, a gesture-driven cursor control system designed to allow users to interact with a computer using hand gestures captured through a standard webcam.

AeroPoint uses computer vision and real-time hand tracking to translate hand movement into cursor actions such as movement, clicking, and scrolling. The system is designed with accessibility, usability, privacy, and maintainability in mind. The project builds on the Capstone I design phase and focuses on moving the system from a design specification into a functional, testable, and user-friendly prototype.

Within this repository, you will find project artifacts and implementation resources, including:

- Source code for the AeroPoint application
- Gesture recognition logic
- Hand-tracking and calibration modules
- Cursor control functionality
- Planned PySide6 graphical user interface components
- Project documentation
- Issues and development tasks
- Milestones for organizing Capstone II work
- Changelog updates
- Testing and validation materials

## Project Overview

AeroPoint is intended to support hands-free or reduced-contact computer interaction by using a webcam to detect hand landmarks and interpret gestures. The system relies on a modular architecture so that individual components can be developed, tested, and improved independently.

The major system components include:

- **Camera Stream Module** – captures webcam frames and handles visual display.
- **Hand Tracking Module** – uses MediaPipe to detect hand landmarks.
- **Gesture Recognition Module** – identifies gestures such as pinch, scroll, and finger-state actions.
- **Calibration Module** – maps the user’s hand movement range to screen coordinates.
- **Cursor Controller** – performs operating system cursor actions using PyAutoGUI.
- **Application Orchestration Module** – coordinates the full real-time processing loop.
- **User Interface Layer** – planned PySide6 interface for calibration, settings, and user feedback.

## Purpose of This Repository

The purpose of this repository is to organize and manage the development of AeroPoint during Capstone II. It serves as the central location for all implementation, testing, documentation, and project tracking activities.

This repository is intended to help the team:

- Maintain a clear and professional project structure
- Track development progress through issues and milestones
- Collaborate efficiently using Git and GitHub/Azure DevOps workflows
- Keep implementation aligned with the approved Capstone I design
- Support future maintainability and extensibility of the system

## Project Goals

The main goals of AeroPoint are:

- Provide real-time cursor control using hand gestures.
- Support basic interaction features such as movement, clicking, and scrolling.
- Improve accessibility for users who may have difficulty using traditional pointing devices.
- Use standard consumer hardware, such as a webcam and laptop, without requiring specialized devices.
- Keep all video processing local to protect user privacy.
- Build a modular and testable system that can support future gesture expansion.

## Planned Capstone II Enhancements

During Capstone II, the project will focus on refining the prototype and improving the user experience. Planned enhancements include:

- Building a dedicated **PySide6 graphical user interface**
- Adding visual indicators for camera status, hand detection, and gesture recognition
- Improving the calibration workflow
- Refining cursor movement smoothing
- Stabilizing pinch-click detection
- Tuning two-finger scroll behavior
- Adding user-configurable settings for sensitivity and scrolling speed
- Improving system safety when hand tracking is lost
- Preparing the system for future gesture expansion

## Technology Stack

The project is planned around the following technologies:

- **Python 3.12**
- **OpenCV** for camera access and frame processing
- **MediaPipe Hands** for hand landmark detection
- **PyAutoGUI** for cursor movement, clicking, and scrolling
- **PySide6** for the planned desktop user interface
- **Git/GitHub or Azure DevOps** for version control and project tracking
