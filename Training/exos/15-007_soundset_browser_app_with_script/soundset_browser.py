#!/usr/bin/env python

import sys
import signal
import qi
import os
import time


class SoundsetBrowserService(object):
    subscriber_list = []
    loaded_topic = ""

    def __init__(self, application):
        # Getting a session that will be reused everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        self.memkey_prefix = "soundset_browser_gr"

        # Getting a logger. Logs will be in /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)

        # Do some initializations before the service is registered to NAOqi
        self.logger.info("Initializing...")
        # @TODO: insert init functions here
        self.create_signals()
        self.logger.info("Initialized!")

    @qi.nobind
    def start_app(self):
        # do something when the service starts
        print "Starting app..."
        # @TODO: insert whatever the app should do to start
        self.show_screen()
        #self.start_dialog()
        self.logger.info("Started!")

    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.application.stop()
        self.logger.info("Stopped!")

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        # @TODO: insert cleaning functions here
        self.disconnect_signals()
        #self.stop_dialog()
        self.hide_screen()
        self.logger.info("Cleaned!")

    @qi.nobind
    def create_signals(self):
        self.logger.info("Creating ColorChosen event...")
        # When you can, prefer qi.Signals instead of ALMemory events
        memory = self.session.service("ALMemory")

        event_name = self.memkey_prefix + "/pageready"
        memory.declareEvent(event_name)
        event_subscriber = memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_event_pageready)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = self.memkey_prefix + "/filenames"
        memory.declareEvent(event_name)
        event_subscriber = memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_event_filenames)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = self.memkey_prefix + "/exit"
        memory.declareEvent(event_name)
        event_subscriber = memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_exit)
        self.subscriber_list.append([event_subscriber, event_connection])

        self.logger.info("Events created!")

    @qi.nobind
    def disconnect_signals(self):
        self.logger.info("Unsubscribing to all events...")
        for sub, i in self.subscriber_list :
            try:
                sub.signal.disconnect(i)
            except Exception, e:
                self.logger.info("Error unsubscribing: {}".format(e))
        self.logger.info("Unsubscribe done!")

    @qi.nobind
    def start_dialog(self):
        self.logger.info("Loading dialog")
        dialog = self.session.service("ALDialog")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        topic_path = os.path.realpath(os.path.join(dir_path, "color", "color_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = dialog.loadTopic(topic_path)
            dialog.activateTopic(self.loaded_topic)
            dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))

    @qi.nobind
    def stop_dialog(self):
        self.logger.info("Unloading dialog")
        try:
            dialog = self.session.service("ALDialog")
            dialog.unsubscribe(self.service_name)
            dialog.deactivateTopic(self.loaded_topic)
            dialog.unloadTopic(self.loaded_topic)
            self.logger.info("Dialog unloaded!")
        except Exception, e:
            self.logger.info("Error while unloading dialog: {}".format(e))

    @qi.nobind
    def show_screen(self):
        folder = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
        self.logger.info("Loading tablet page for app: {}".format(folder))
        try:
            ts = self.session.service("ALTabletService")
            ts.loadApplication(folder)
            ts.showWebview()
            self.logger.info("Tablet loaded!")
        except Exception, e:
            self.logger.info("Error while loading tablet: {}".format(e))

    @qi.nobind
    def hide_screen(self):
        self.logger.info("Unloading tablet...")
        try:
            tablet = self.session.service("ALTabletService")
            tablet.hideWebview()
            self.logger.info("Tablet unloaded!")
        except Exception, e:
            self.logger.info("Error while unloading tablet: {}".format(e))

    @qi.bind(methodName="onEventPageready", paramsType=(qi.String,), returnType=qi.Void)
    def on_event_pageready(self, value):
        self.logger.info("function on_event_pageready called")
        self.audio_player_service = self.session.service("ALAudioPlayer")
        self.memory = self.session.service("ALMemory")

        # list the soundsets
        existing_soundsets = self.audio_player_service.getInstalledSoundSetsList()

        # load the soundsets
        for exsoundset in existing_soundsets:
            self.audio_player_service.loadSoundSet(exsoundset)

        # list loaded soundets
        loaded_soundsets   = self.audio_player_service.getLoadedSoundSetsList()

        sounds_list = list()

        for soundset in loaded_soundsets:
            filenames = self.audio_player_service.getSoundSetFileNames(soundset)

            sounds_list.extend(filenames)
            #audio_player_service.playSoundSetFile(soundset, f, _async=True)
         
        self.logger.info("Sound list : ")   
        self.logger.info(sounds_list)
        self.memory.raiseEvent( self.memkey_prefix + "/filenames", sounds_list)

    @qi.bind(methodName="onEventFilenames", paramsType=(qi.String,), returnType=qi.Void)
    def on_event_filenames(self, value):
        self.logger.info("Filenames list sent to web page")
        pass

    @qi.bind(methodName="onExit", returnType=qi.Void)
    def on_exit(self, value):
        self.stop_app()
            
if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = SoundsetBrowserService(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)
