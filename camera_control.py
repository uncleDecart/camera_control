from time import sleep
from onvif import ONVIFCamera

import credentials 

debug_mode = False

class ipCamera:
    def __init__(self, ip, port, usr, pswd, wsdl_path):
        # Monkey coded to pass error
        self.cam = ONVIFCamera(ip,port,usr, pswd, wsdl_path)
        
        if debug_mode:
            self.print_trace("Camera information : "
                             +str(self.cam.devicemgmt.GetDeviceInformation()))
            self.print_trace("Camera hostname :"+str(self.cam.devicemgmt.GetHostname().Name))
       
        self.media_service = self.cam.create_media_service()
        self.media_profile = self.media_service.GetProfiles()[0]
        
        if debug_mode:
            self.print_trace("Media service profiles : " + str(self.media_service.GetProfiles()))

        self.ptz = self.cam.create_ptz_service()
       
        if debug_mode:
            req = self.ptz.create_type('GetServiceCapabilities')
            ser_cap = self.ptz.GetServiceCapabilities(req)
            self.print_trace("Service capabilities: "+str(ser_cap))
            
            req = self.ptz.create_type('GetConfigurationOptions')
            req.ConfigurationToken = self.media_profile.PTZConfiguration.token
            ptz_opt = self.ptz.GetConfigurationOptions(req)
            self.print_trace("Configuration options : "+str(ptz_opt))
        
        self.absolute_move = self.ptz.create_type('AbsoluteMove')
        self.absolute_move.ProfileToken = self.media_profile.token

        self.relative_move = self.ptz.create_type('RelativeMove')
        self.relative_move.ProfileToken = self.media_profile.token

        self.continous_move = self.ptz.create_type('ContinuousMove')
        self.continous_move.ProfileToken = self.media_profile.token

        self.req_stop = self.ptz.create_type('Stop')
        self.req_stop.ProfileToken = self.media_profile.token

        self.imaging = self.cam.create_imaging_service()
        
        if debug_mode:
            req = self.imaging.create_type('GetServiceCapabilities')
            ser_cap = self.ptz.GetServiceCapabilities(req)
            self.print_trace("Imaging service cap : "+str(ser_cap))

            status = self.imaging.GetStatus({'VideoSourceToken' :
                self.media_profile.VideoSourceConfiguration.SourceToken})

            self.print_trace("Status"+str(status))
        
        self.focus = self.imaging.create_type("Move")
        self.focus.VideoSourceToken=self.media_profile.VideoSourceConfiguration.SourceToken

        self.action_timeout = 3

    def print_trace(self, string):
        print(string)
        print(80*'=')

    def stop(self):
        self.req_stop.PanTilt = True
        self.req_stop.Zoom = True

        self.ptz.Stop(self.req_stop)

    def perform_continous(self, timeout):
        self.ptz.ContinuousMove(self.continous_move)

        sleep(timeout)

        self.stop()

        sleep(self.action_timeout)

    def move_continous(self, tiltX, tiltY, timeout):
        print("CMoving with tiltX: {0} tiliY: {1} timeout {2}".format(tiltX, tiltY, timeout))

        status = self.ptz.GetStatus({'ProfileToken' : self.media_profile.token})
        status.Position.PanTilt.x = tiltX
        status.Position.PanTilt.y = tiltY
        
        self.continous_move.Velocity = status.Position

        self.perform_continous(timeout)

    def zoom(self, xVelocity, timeout):
        print("Zooming with xVelocity: {0} timeout: {1}".format(xVelocity, timeout))

        status = self.ptz.GetStatus({'ProfileToken' : self.media_profile.token})
        status.Position.Zoom.x = velocity

        self.continous_move.Velocity = status.Position

        self.perform_continous(timeout)


    def move_absolute(self, x, y, zoom):
        print("AMoving with x: {0} y: {1} zoom: {2}".format(x, y, zoom))

        status = self.ptz.GetStatus({'ProfileToken' : self.media_profile.token})
        status.Position.PanTilt.x = x
        status.Position.PanTilt.y = y
        status.Position.Zoom = zoom

        self.absolute_move.Position = status.Position
        self.ptz.AbsoluteMove(self.absolute_move)

        sleep(self.action_timeout)

    def cont_focus(self, speed, timeout):
        self.focus.Focus = {"Continuous" : {"Speed" : speed}}
        self.imaging.Move(self.focus)
        sleep(timeout)
        self.stop()
        
        sleep(self.action_timeout)

    def abs_focus(self, pos, speed):
        self.focus.Focus = {"Absolute" : {"Position" : pos,"Speed" : speed}}
        self.imaging.Move(self.focus)
        
        sleep(self.action_timeout)

    def rel_focus(self, dist, speed):
        self.focus.Focus = {"Relative" : {"Distance" : dist,"Speed" : speed}}
        self.imaging.Move(self.focus)
        
        sleep(self.action_timeout)


cam = ipCamera(credentials.camera43, 80,
               credentials.user,
               credentials.paswd,
               credentials.lib_path) 

timeout = 1
cam.move_continous(0, 1,timeout)
cam.move_continous(0, -1, timeout)
cam.move_continous(1, 0, timeout)
cam.move_continous(-1, 0, timeout)

cam.move_absolute(0.1, -0.5, 0)

cam.cont_focus(-0.5, 1)
cam.cont_focus(0.5, 1)
