import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from ..entities import Booking, Room, Service, Staff

class ReportGenerator():
    """
    Generate reports for the Manager. 

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: 4-28-25
        Modified: 4-29-25
    """

    __instance = None

    def __new__(cls):
        """
        Ensures that only a single instance of the ReportGenerator class is created (singleton design pattern).
        If the instance does not already exist, it creates a new instance, else it returns the existing instance.

        Parameters:
            None

        Returns:
            ReportGenerator: The single ReportGenerator instance. 
        """
        if cls.__instance is None:
            cls.__instance = super(ReportGenerator, cls).__new__(cls)
        return cls.__instance
    
    @staticmethod
    def empty_figure(title):
        """
        Returns a blank bar graph. 

        Parameters:
            title (str): The title for the bar graph. 
        
        Returns:
            str: A JSON-encoded string of the Plotly bar graph.
        """
        empty_figure = px.bar(title=title)
        empty_figure = json.dumps(empty_figure, cls=plotly.utils.PlotlyJSONEncoder)
        return empty_figure
    
    @classmethod
    def get_service_stats(cls, location=None, startdate=None, enddate=None):
        """
        Returns a pie chart of service request frequencies. 
        Filters by optional location and date range. 

        Parameters:
            location (str, optional): The hotel's location.
            startdate (datetime, optional): Start of the date range.
            enddate (datetime, optional): End of the date range.
        
        Returns:
            str: A JSON-encoded string of the Plotly pie chart if service data exists, else an empty bar graph.
        """
        service_frequency = Service.get_service_stats(location, startdate, enddate)
        if service_frequency:
            labels = [service[0].value for service in service_frequency]
            values = [service[1] for service in service_frequency]
            figure = px.pie(names=labels, values=values, title='Service Request Frequencies')
            figure.update_layout(legend=dict(orientation='h', y=-0.05, x=0.5, xanchor='center'), height=500,
                                margin=dict(t=100,b=100,l=50,r=50), title_x=0.5)
            graph = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
            return graph
        else:
            return cls.empty_figure("No Service Data Found")
    
    @classmethod
    def get_booking_stats(cls, location=None, startdate=None, enddate=None):
        """
        Returns a digit-figure of revenue (based on completed and pending bookings)
        Filters by optional location and date range. 

        Parameters:
            location (str, optional): The hotel's location.
            startdate (datetime, optional): Start of the date range.
            enddate (datetime, optional): End of the date range.
        
        Returns:
            tuple: Two JSON-encoded strings (one for completed bookings and the other for pending bookings) of the Plotly indicator chart if booking data exists, else an empty bar graph.
        """
        completed, pending = Booking.get_booking_stats(location, startdate, enddate)
        if completed and pending:
            completed_figure = go.Figure()
            completed_figure.add_trace(go.Indicator(mode="number", value=(completed.total_fees or 0), title={"text":"Total Earned Revenue"}, domain={'x':[0,0.5], 'y':[0,1]}))
            completed_figure.add_trace(go.Indicator(mode="number", value=(completed.total_bookings or 0), title={"text":"Total Completed Bookings"}, domain={'x':[0.5,1], 'y':[0,1]}))
            completed_figure.update_layout(legend=dict(orientation='h', y=-0.05, x=0.5, xanchor='center'), height=300,
                                margin=dict(t=50,b=50,l=50,r=50), title_x=0.5)
            completed_figure = json.dumps(completed_figure, cls=plotly.utils.PlotlyJSONEncoder)

            pending_figure = go.Figure()
            pending_figure.add_trace(go.Indicator(mode="number", value=(pending.total_fees or 0), title={"text":"Total Pending Revenue"}, domain={'x':[0,0.5], 'y':[0,1]}))
            pending_figure.add_trace(go.Indicator(mode="number", value=(pending.total_bookings or 0), title={"text":"Total Pending Bookings"}, domain={'x':[0.5,1], 'y':[0,1]}))
            pending_figure.update_layout(legend=dict(orientation='h', y=-0.05, x=0.5, xanchor='center'), height=300,
                                margin=dict(t=50,b=50,l=50,r=50), title_x=0.5)
            pending_figure = json.dumps(pending_figure, cls=plotly.utils.PlotlyJSONEncoder)

            return completed_figure, pending_figure
        else:
            return cls.empty_figure("No Booking Data Found")
    
    @classmethod
    def get_room_popularity_stats(cls, location=None, startdate=None, enddate=None):
        """
        Returns a bar graph of most popular rooms
        Filters by optional location and date range. 

        Parameters:
            location (str, optional): The hotel's location.
            startdate (datetime, optional): Start of the date range.
            enddate (datetime, optional): End of the date range.
        
        Returns:
            str: A JSON-encoded string of the Plotly bar graph if room-booking data exists, else an empty bar graph.
        """
        popularity = Booking.get_room_popularity_stats(location, startdate, enddate) #row objects with (rid, popularity)
        if popularity:
            popularity_list = []
            for row in popularity:
                room = Room.get_room(row[0])
                if room:
                    desc = room.get_room_description()
                    hid = room.get_room_hotel()
                    abbrieviated = ' '.join(desc.split(' ')[:2])
                    popularity_list.append({
                        "room":abbrieviated,
                        "description": desc,
                        "count":row[1],
                        "hid": str(hid)
                    })
                else:
                    popularity_list.append({
                        "room":'N/A',
                        "description":'N/A',
                        "count":row[1],
                        "hid":'N/A'
                    })

            popularity_figure = px.bar(popularity_list, x="room",y="count",title="Room Popularity", color="hid",labels={'room':'Room','count':'Number of Bookings', 'description':'Full Description', 'hid': 'Hotel ID'},
                                       hover_data=["description", "hid"])
            popularity_figure.update_layout(height=800, margin=dict(t=100,b=100,l=50,r=50), title_x=0.5)
            popularity_figure = json.dumps(popularity_figure, cls=plotly.utils.PlotlyJSONEncoder)
            return popularity_figure
        else:
            return cls.empty_figure("No Room Data Found")
    
    @classmethod
    def get_staff_insights(cls, location=None, startdate=None, enddate=None, assignable_staff=None):
        """
        Returns a bar graph of staff task-completion insights. 
        Filters by optional location, date range, and staff members to be included in the analysis.  

        Parameters:
            location (str, optional): The hotel's location.
            startdate (datetime, optional): Start of the date range.
            enddate (datetime, optional): End of the date range.
            assignable_staff (list[Staff], optional): List of staff to be included in the analysis.

        Returns:
            tuple: A JSON-encoded string of the Plotly bar graph if service-staff data exists, else an empty bar graph.
        """
        staff_insights = Service.get_staff_insights(location, startdate, enddate, assignable_staff)
        if staff_insights:
            staff_insights_list = [{"staff":Staff.get_staff(row[0]).get_name().upper() if row[0] else 'Unknown', 'status':row[1].value,'count':row[2]} for row in staff_insights]
            staff_figure = px.bar(staff_insights_list, x="staff",y="count",title="Staff Efficiency", labels={'staff':'Staff','count':'Activity', 'status':'Status'}, color="status")
            staff_figure = json.dumps(staff_figure, cls=plotly.utils.PlotlyJSONEncoder)
            return staff_figure
        else:
            return cls.empty_figure("No Staff Data Found")
