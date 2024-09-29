import UIKit
import Flutter
import AVFoundation
import MediaPlayer // Add this import statement

@main
@objc class AppDelegate: FlutterAppDelegate {
    
    private var audioSession: AVAudioSession!
    private var volumeView: MPVolumeView!
    private var lastVolume: Float = 0.5 // Default initial volume
    
    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        let controller: FlutterViewController = window?.rootViewController as! FlutterViewController
        let volumeChannel = FlutterMethodChannel(name: "com.example.formosa_app.volume_buttons",
                                                 binaryMessenger: controller.binaryMessenger)

        // Set up volume button listener
        setupVolumeButtonListener()

        // No method handler for now, we are just sending events to Flutter
        volumeChannel.setMethodCallHandler { (call: FlutterMethodCall, result: @escaping FlutterResult) in
            // Handle method calls from Flutter if needed
        }
        
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
    
    private func setupVolumeButtonListener() {
        // Initialize audio session and start observing volume changes
        audioSession = AVAudioSession.sharedInstance()
        
        do {
            try audioSession.setActive(true)
            lastVolume = audioSession.outputVolume
            NotificationCenter.default.addObserver(self, selector: #selector(volumeChanged(_:)),
                                                   name: NSNotification.Name("AVSystemController_SystemVolumeDidChangeNotification"), object: nil)
        } catch {
            print("Error activating audio session: \(error)")
        }
        
        // Add a hidden MPVolumeView to block the system volume UI
        volumeView = MPVolumeView(frame: CGRect(x: -1000, y: -1000, width: 0, height: 0))
        window?.rootViewController?.view.addSubview(volumeView)
    }
    
    @objc private func volumeChanged(_ notification: Notification) {
        guard let userInfo = notification.userInfo,
              let volumeChangeType = userInfo["AVSystemController_AudioVolumeChangeReasonNotificationParameter"] as? String,
              let newVolume = userInfo["AVSystemController_AudioVolumeNotificationParameter"] as? Float else {
            return
        }

        // Detect volume up or down
        let isVolumeUp = newVolume > lastVolume
        lastVolume = newVolume
        
        let volumeType = isVolumeUp ? "volume_up" : "volume_down"
        
        // Send the event to Flutter
        let volumeChannel = FlutterMethodChannel(name: "com.example.formosa_app.volume_buttons",
                                                 binaryMessenger: (window?.rootViewController as! FlutterViewController).binaryMessenger)
        volumeChannel.invokeMethod("onVolumeButtonPressed", arguments: ["button": volumeType, "pressType": "short"])
    }
}
