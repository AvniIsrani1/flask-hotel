import plotly
import plotly.express as px
import plotly.graph_objects as go
import json

class ReportGenerator():
    """
    Generate reports for the Manager. 

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: 4-28-25
        Modified: 4-29-25
    """
    
    def get_service_stats():
        """
        Returns a pie chart of service request frequencies. 
        """
        from ..entities import Service
        service_frequency = Service.get_service_stats()
        labels = [service[0].value for service in service_frequency]
        values = [service[1] for service in service_frequency]
        figure = px.pie(names=labels, values=values, title='Service Request Frequencies')
        figure.update_layout(legend=dict(orientation='h', y=-0.05, x=0.5, xanchor='center'), height=500,
                             margin=dict(t=100,b=100,l=50,r=50), title_x=0.5)
        graph = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
    
    def get_booking_stats():
        """
        Returns a digit-figure of revenue (based on completed and pending bookings)
        """
        from ..entities import Booking
        completed, pending = Booking.get_booking_stats()
        completed_figure = go.Figure()
        completed_figure.add_trace(go.Indicator(mode="number", value=(completed.total_fees or 0), title={"text":"Total Completed Revenue"}, domain={'x':[0,0.5], 'y':[0,1]}))
        completed_figure.add_trace(go.Indicator(mode="number", value=(completed.total_bookings or 0), title={"text":"Total Completed Bookings"}, domain={'x':[0.5,1], 'y':[0,1]}))
        completed_figure = json.dumps(completed_figure, cls=plotly.utils.PlotlyJSONEncoder)

        pending_figure = go.Figure()
        pending_figure.add_trace(go.Indicator(mode="number", value=(pending.total_fees or 0), title={"text":"Total Pending Revenue"}, domain={'x':[0,0.5], 'y':[0,1]}))
        pending_figure.add_trace(go.Indicator(mode="number", value=(pending.total_bookings or 0), title={"text":"Total Pending Bookings"}, domain={'x':[0.5,1], 'y':[0,1]}))
        pending_figure = json.dumps(pending_figure, cls=plotly.utils.PlotlyJSONEncoder)
        return completed_figure, pending_figure
    
    def get_room_popularity_stats():
        """
        Returns a bar graph of most popular rooms
        """
        from ..entities import Booking
        from ..entities import Room
        
        popularity = Booking.get_room_popularity_stats() #row objects with (rid, popularity)
        popularity_list = [{"room":(Room.get_room(row[0]).get_room_description() if Room.get_room(row[0]) else 'N/A'), "count":row[1]} for row in popularity]

        popularity_figure = px.bar(popularity_list, x="room",y="count",title="Room Popularity",labels={'room':'Room','count':'Number of Bookings'}, color="room")
        popularity_figure = json.dumps(popularity_figure, cls=plotly.utils.PlotlyJSONEncoder)
        return popularity_figure
