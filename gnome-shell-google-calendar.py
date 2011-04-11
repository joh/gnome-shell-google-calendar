#!/usr/bin/python 
# -*- coding: utf-8 -*-
from datetime import datetime
from time import mktime

import gtk
import dbus
import dbus.service
import dbus.mainloop.glib
import gdata.calendar.client
 
class CalendarService(dbus.service.Object):
    busname = 'org.gnome.Shell.CalendarServer'
    object_path = '/org/gnome/Shell/CalendarServer'

    def __init__(self):
        bus = dbus.service.BusName(self.busname,
                                        bus=dbus.SessionBus(),
                                        replace_existing=True)

        super(CalendarService, self).__init__(bus, self.object_path)
 
    @dbus.service.method('org.gnome.Shell.CalendarServer',
                         in_signature='xxb', out_signature='a(sssbxxa{sv})')
    def GetEvents(self, since, until, force_reload):
        events = []

        calendar_client = gdata.calendar.client.CalendarClient()
        username = 'jvajen@gmail.com'
        visibility = 'private-a87abd05c51ecabeec71316e76348a4d'
        projection = 'full'

        feed_uri = calendar_client.GetCalendarEventFeedUri(
                                                        calendar=username, 
                                                        visibility=visibility,
                                                        projection=projection)

        feed = calendar_client.GetCalendarEventFeed(uri=feed_uri)

        for event in feed.entry:
            for when in event.when:
                wholeday = False
                isoformat = "%Y-%m-%dT%H:%M:%S.%f"

                try:
                    start = datetime.strptime(when.start.split('+')[0], isoformat)
                    start = int(mktime(start.timetuple()))
                    end = datetime.strptime(when.end.split('+')[0], isoformat)
                    end = int(mktime(end.timetuple()))
                except ValueError:
                    wholeday = True

                events.append(('', 
                               str(event.title.text), 
                               '', 
                               wholeday,
                               start, 
                               end, 
                               {}))

        return events

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    myservice = CalendarService()
    gtk.main()
