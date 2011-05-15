#!/usr/bin/python 
# -*- coding: utf-8 -*-
from datetime import datetime
from time import mktime

import gtk
import dbus
import dbus.service
import dbus.mainloop.glib
from gdata.calendar.service import CalendarService, CalendarEventQuery
import iso8601

class CalendarServer(dbus.service.Object):
    busname = 'org.gnome.Shell.CalendarServer'
    object_path = '/org/gnome/Shell/CalendarServer'
    
    def __init__(self, email, password):
        bus = dbus.service.BusName(self.busname,
                                        bus=dbus.SessionBus(),
                                        replace_existing=True)

        super(CalendarServer, self).__init__(bus, self.object_path)
        
        self.client = CalendarService()
        self.client.email = email
        self.client.password = password
        
        self.authenticate()
        
        self.calendars = self.get_calendars()
    
    def authenticate(self):
        self.client.source = 'github-gnome_shell_google_calendar-0.1'
        self.client.ProgrammaticLogin()
    
    def get_calendars(self):
        feed = self.client.GetAllCalendarsFeed()
        
        calendars = []
        
        print feed.title.text + ':'
        
        for calendar in feed.entry:
            print '  ', calendar.title.text
            print '    ', calendar.content.src
            
            calendars.append((calendar.title.text, calendar.content.src))
        
        return calendars
    
    def parse_time(self, timestr):
        try:
            time = datetime.strptime(timestr, '%Y-%m-%d')
            allday = True
        except ValueError:
            time = iso8601.parse_date(timestr)
            allday = False
        
        time = int(mktime(time.timetuple()))
        
        return (time, allday)
    
    
    @dbus.service.method('org.gnome.Shell.CalendarServer',
                         in_signature='xxb', out_signature='a(sssbxxa{sv})')
    def GetEvents(self, since, until, force_reload):
        print "GetEvents(since=%s, until=%s, force_reload=%s)" % \
                (since, until, force_reload)
        
        since_date = datetime.fromtimestamp(since)
        until_date = datetime.fromtimestamp(until)
        print "  since:", since_date.strftime('%Y-%m-%d')
        print "  until:", until_date.strftime('%Y-%m-%d')
        
        events = []
        
        for calendar, feed_url in self.calendars:
            print 'Getting events from', calendar, '...'
            
            query = CalendarEventQuery()
            query.feed = feed_url
            query.start_min = since_date.strftime('%Y-%m-%d')
            query.start_max = until_date.strftime('%Y-%m-%d')
            feed = self.client.CalendarQuery(query)
            
            for event in feed.entry:
                print '  ', event.title.text
                title = event.title.text
                
                for when in event.when:
                    print '    ', when.start_time, 'to', when.end_time
                    
                    allday = False
                    
                    start, allday = self.parse_time(when.start_time)
                    end, _ = self.parse_time(when.end_time)
                    
                    events.append(('',      # uid
                                   title,   # summary
                                   '',      # description
                                   allday,  # allDay
                                   start,   # date
                                   end,     # end
                                   {}))     # extras
        
        print 'returning'
        
        return events

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    myserver = CalendarServer('email', 'password')
    gtk.main()
