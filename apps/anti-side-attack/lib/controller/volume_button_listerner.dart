import 'package:flutter/services.dart';

class VolumeButtonListener {
  static const _platform = MethodChannel('com.example.formosa_app.volume_buttons');

  static Future<void> listenForVolumeButtonPress(Function(VolumeButtonEvent) onVolumeButtonEvent) async {
    _platform.setMethodCallHandler((call) async {
      if (call.method == 'onVolumeButtonPressed') {
        final int buttonValue = call.arguments['button'];
        final String pressTypeValue = call.arguments['pressType'];

        VolumeButton button = buttonValue == 1 ? VolumeButton.up : VolumeButton.down;
        PressType pressType = pressTypeValue.contains('short') ? PressType.shortPress : PressType.longPress;

        onVolumeButtonEvent(VolumeButtonEvent(
          button: button,
          pressType: pressType,
        ));
      }
    });
  }
}

class VolumeButtonEvent {
  final VolumeButton button;
  final PressType pressType;

  VolumeButtonEvent({
    required this.button,
    required this.pressType,
  });
}

enum PressType {
  shortPress,
  longPress,
}

enum VolumeButton {
  up, // 1 represents 'up'
  down, // 0 represents 'down'
}

extension VolumeButtonExtension on VolumeButton {
  String get value => this == VolumeButton.up ? '1' : '0';
  bool get isUp => this == VolumeButton.up;
  bool get isDown => this == VolumeButton.down;
}
extension PressTypeExtension on PressType {
  String get value => this == PressType.shortPress ? 'short' : 'long';
  bool get isShortPress => this == PressType.shortPress;
  bool get isLongPress => this == PressType.longPress;
}
