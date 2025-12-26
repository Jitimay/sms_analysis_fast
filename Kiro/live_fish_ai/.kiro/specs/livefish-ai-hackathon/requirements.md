# LiveFish AI Hackathon Requirements Document

## Introduction

LiveFish AI is an offline, real-time mobile AI application designed for the ARM Hackathon that helps fishermen and conservationists identify fish species and measure their size directly through a smartphone camera. The application leverages an optimized YOLOv8 Nano model running on Arm-based Android devices to detect fish in live video streams, estimate size using AR techniques, and store ecological data locally. This project addresses sustainable fishing practices while demonstrating advanced on-device AI capabilities on Arm architecture.

## Requirements

### Requirement 1: Real-time Fish Detection

**User Story:** As a fisherman, I want to point my phone camera at a fish and see it detected in real-time, so that I can quickly identify whether I'm looking at a fish without manual inspection.

#### Acceptance Criteria

1. WHEN the user opens the camera view THEN the system SHALL display live camera feed with real-time processing
2. WHEN a fish appears in the camera frame THEN the system SHALL detect it within 100ms and display a bounding box
3. WHEN the fish detection confidence is above 70% THEN the system SHALL display the detection with a green bounding box
4. WHEN the fish detection confidence is below 70% THEN the system SHALL display the detection with a yellow bounding box
5. WHEN no fish is detected THEN the system SHALL display clean camera feed without any overlays

### Requirement 2: AI Model Integration on Arm Architecture

**User Story:** As a developer, I want to run an optimized YOLOv8 model on Arm-based devices, so that the application demonstrates efficient on-device AI processing.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL load a YOLOv8 Nano TensorFlow Lite model (≤6MB)
2. WHEN processing camera frames THEN the system SHALL achieve inference time ≤50ms on Arm NPU/CPU
3. WHEN running on Snapdragon, MediaTek, or Unisoc processors THEN the system SHALL utilize Arm architecture optimizations
4. WHEN the model processes 320x320 input images THEN the system SHALL maintain ≥85% detection accuracy
5. WHEN the device has limited memory THEN the system SHALL operate within 100MB RAM usage

### Requirement 3: AR-based Size Measurement

**User Story:** As a fisherman, I want to measure the size of detected fish using my phone's camera, so that I can determine if the fish meets size regulations without physical measurement.

#### Acceptance Criteria

1. WHEN a fish is detected THEN the system SHALL provide an option to measure its length
2. WHEN the user places a reference object (coin, card) in frame THEN the system SHALL calibrate the measurement scale
3. WHEN the user taps "Measure" THEN the system SHALL calculate and display fish length in centimeters
4. WHEN using ARCore-enabled devices THEN the system SHALL utilize depth estimation for improved accuracy
5. WHEN measurement is complete THEN the system SHALL display the result with ±2cm accuracy indication

### Requirement 4: Offline Data Storage and Logging

**User Story:** As a conservationist, I want to log fish catches with size, location, and timestamp data offline, so that I can contribute to biodiversity research even without internet connectivity.

#### Acceptance Criteria

1. WHEN a fish is detected and measured THEN the system SHALL provide a "Log Catch" button
2. WHEN the user logs a catch THEN the system SHALL store fish size, GPS coordinates, timestamp, and confidence score locally
3. WHEN the device is offline THEN the system SHALL continue logging data to local storage (Hive/SQLite)
4. WHEN the user views catch history THEN the system SHALL display all logged catches with filtering options
5. WHEN storage reaches 80% capacity THEN the system SHALL notify the user and offer data export options

### Requirement 5: Cross-platform Mobile Application

**User Story:** As a user, I want to install and run LiveFish AI on my Android device, so that I can use the fish detection capabilities on my existing smartphone.

#### Acceptance Criteria

1. WHEN the user installs the APK THEN the system SHALL run on Android 7.0+ devices with Arm processors
2. WHEN the application launches THEN the system SHALL request camera and location permissions appropriately
3. WHEN the user navigates the app THEN the system SHALL provide intuitive Flutter-based UI with smooth transitions
4. WHEN the device orientation changes THEN the system SHALL maintain camera feed and detection functionality
5. WHEN the app runs in background THEN the system SHALL pause AI processing to conserve battery

### Requirement 6: Open Source Compliance and Documentation

**User Story:** As a hackathon participant, I want to provide complete source code and documentation, so that judges can evaluate and other developers can build upon the project.

#### Acceptance Criteria

1. WHEN the project is submitted THEN the system SHALL include a public GitHub repository with open source license
2. WHEN developers access the repository THEN the system SHALL provide step-by-step build instructions for Arm devices
3. WHEN the code is reviewed THEN the system SHALL demonstrate clean architecture with proper documentation
4. WHEN the project is built THEN the system SHALL compile successfully on Flutter development environment
5. WHEN the documentation is read THEN the system SHALL clearly explain AI model integration and Arm optimizations

### Requirement 7: Performance Optimization for Hackathon Demo

**User Story:** As a hackathon presenter, I want the application to perform reliably during demonstrations, so that I can showcase the full capabilities to judges effectively.

#### Acceptance Criteria

1. WHEN demonstrating live detection THEN the system SHALL maintain consistent 15-20 FPS camera processing
2. WHEN multiple fish appear in frame THEN the system SHALL detect and track up to 3 fish simultaneously
3. WHEN the demo runs for 10+ minutes THEN the system SHALL maintain stable performance without crashes
4. WHEN switching between features THEN the system SHALL respond within 500ms for all UI interactions
5. WHEN presenting to judges THEN the system SHALL work reliably on the target demo device

### Requirement 8: Conservation Impact Features

**User Story:** As an environmental advocate, I want to see how the application promotes sustainable fishing, so that I can understand its conservation value beyond the technical implementation.

#### Acceptance Criteria

1. WHEN a small fish is detected (below minimum size threshold) THEN the system SHALL display a conservation warning
2. WHEN the user logs catches over time THEN the system SHALL show statistics about fish sizes and catch frequency
3. WHEN the application is used THEN the system SHALL provide educational tips about sustainable fishing practices
4. WHEN data is collected THEN the system SHALL prepare it in a format suitable for research contribution
5. WHEN the user views impact metrics THEN the system SHALL display their contribution to conservation efforts