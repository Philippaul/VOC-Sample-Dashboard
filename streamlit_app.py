import sys
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
  page_title="VOC αlpha - JLR",
  layout='wide',
  initial_sidebar_state='expanded',
  page_icon="JLR_Blue_Logo.svg"
)

# Load custom CSS
with open('style.css') as f:
  st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("""
<style>
    .custom-container {
        background-color: #2ecc71;
        padding: 30px;
        border-radius: 15px;
        color: white;
    }
    .custom-container h2 {
        color: #1c3b3a;
    }
</style>
""", unsafe_allow_html=True)

# Load sample data
seattle_weather = pd.read_csv(
  'https://raw.githubusercontent.com/tvst/plost/master/data/seattle-weather.csv',
  parse_dates=['date']
)
stocks = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/stocks_toy.csv')


# Snowflake connection parameters
SNOWFLAKE_CONFIG = {
  'user': 'PARUNODH',
  'password': 'Philip@2001',
  'account': 'bgnbixy-gl47952',
  'warehouse': 'VOC_WAREHOUSE',
  'database': 'VOC_DASH_DUMMY_DB',
  'schema': 'VOC_VEHICLE'
}

def get_snowflake_connection():
  try:
      # Create connection using embedded parameters
      conn = snowflake.connector.connect(
          user=SNOWFLAKE_CONFIG['user'],
          password=SNOWFLAKE_CONFIG['password'],
          account=SNOWFLAKE_CONFIG['account'],
          warehouse=SNOWFLAKE_CONFIG['warehouse'],
          database=SNOWFLAKE_CONFIG['database'],
          schema=SNOWFLAKE_CONFIG['schema']
      )
      return conn
  except Exception as e:
      print(f"Error connecting to Snowflake: {str(e)}")
      sys.exit(1)


def main():
  pages = {
      "Security Dashboard": Events_Dashboard,
      "Diagnostic Search": Search_Page,
  }

  with st.sidebar:
      st.markdown('<div class="title-container"><h1>Jaguar Land Rover αlpha</h1></div>', unsafe_allow_html=True)

      if 'selected_page' not in st.session_state:
          st.session_state.selected_page = "Security Dashboard"

      st.session_state.selected_page = st.selectbox(
          "Navigate to",
          list(pages.keys()),
          index=list(pages.keys()).index(st.session_state.selected_page),
          label_visibility="collapsed"
      )

      st.divider()
      st.header("Action Center")

      with st.container():
          col1, col2 = st.columns(2)
          with col1:
              st.button("War Room", use_container_width=True)
              st.button("Attack", use_container_width=True)
          with col2:
              st.button("Health Check", use_container_width=True)
              st.button("Defence", use_container_width=True)

      st.sidebar.markdown('---')
      st.sidebar.markdown('''
      Created by Cyber Security Team
      ---
      ''')
      st.sidebar.markdown("""
          <div class="sidebar-footer">
              <p class="footer-text">© 2024 <i>Jaguar Land Rover</i>  <br> <i>Confidential & Internal</i></p>
              <div class="footer-links">
                  <a href="https://www.jaguarlandrover.com/privacy">Privacy</a>
                  <a href="https://www.jaguarlandrover.com/terms-and-conditions">Terms</a>
                  <a href="https://www.jaguarlandrover.com/contact-us">Support</a>
              </div>
          </div>
      """, unsafe_allow_html=True)

  page_function = pages[st.session_state.selected_page]
  page_function()

  st.markdown('---')

def get_snowflake_data():
  try:
      conn = get_snowflake_connection()
      cur = conn.cursor()
      
      # Query for vehicle counts by location
      location_query = """
      SELECT LOCATION, 
             COUNT(DISTINCT VIN_NUMBER) AS total_count
      FROM VEHICLE_DETAILS_DYNAMIC
      GROUP BY LOCATION;
      """
      cur.execute(location_query)
      location_results = cur.fetchall()
      
      # Create a dictionary for location data
      data = {row[0]: {'total_count': row[1]} for row in location_results}
      total_vehicles = sum(row[1] for row in location_results)

      # Query for ticket status counts
      ticket_query = """
      SELECT STATUS, 
             EXTRACT(YEAR FROM CREATED_TIME) AS YEAR, 
             COUNT(*) AS COUNT
      FROM TICKETS_DETAILS_DYNAMIC
      GROUP BY STATUS, YEAR;
      """
      cur.execute(ticket_query)
      ticket_results = cur.fetchall()
      columns = [desc[0] for desc in cur.description]
      ticket_df = pd.DataFrame(ticket_results, columns=columns)

      return data, total_vehicles, ticket_df  # Return all three values
  except Exception as e:
      st.error(f"Database connection error: {str(e)}")
      return {}, 0, pd.DataFrame()
  finally:
      if 'cur' in locals():
          cur.close()
      if 'conn' in locals():
          conn.close()

def execute_snowflake_query(query):
  try:
      conn = snowflake.connector.connect(
          user='PARUNODH',
          password='Philip@2001',
          account='bgnbixy-gl47952',
          warehouse='VOC_WAREHOUSE',
          database='VOC_DASH_DUMMY_DB',
          schema='VOC_VEHICLE'
      )
      cur = conn.cursor()
      cur.execute(query)
      results = cur.fetchall()
      columns = [desc[0] for desc in cur.description]
      return pd.DataFrame(results, columns=columns)
  except Exception as e:
      st.error(f"Database connection error: {str(e)}")
      return pd.DataFrame()
  finally:
      if 'cur' in locals():
          cur.close()
      if 'conn' in locals():
          conn.close()

def get_security_event_status():
  try:
      conn = get_snowflake_connection()
      cur = conn.cursor()
      
      # Query to get counts based on severity
      severity_query = """
      SELECT 
          COUNT(*) AS total,
          SUM(CASE WHEN SEVERITY = 'Critical' THEN 1 ELSE 0 END) AS critical,
          SUM(CASE WHEN SEVERITY = 'Severe' THEN 1 ELSE 0 END) AS severe,
          SUM(CASE WHEN SEVERITY = 'High' THEN 1 ELSE 0 END) AS high,
          SUM(CASE WHEN SEVERITY = 'Low' THEN 1 ELSE 0 END) AS low,
          SUM(CASE WHEN SEVERITY = 'Non-Critical' THEN 1 ELSE 0 END) AS non_critical
      FROM TICKETS_DETAILS_DYNAMIC
      """
      
      cur.execute(severity_query)
      result = cur.fetchone()
      
      # Unpack the result
      total, critical, severe, high, low, non_critical = result
      
      return total, critical, severe, high, low, non_critical
      
  except Exception as e:
      st.error(f"Database connection error: {str(e)}")
      return 0, 0, 0, 0, 0, 0
  finally:
      if 'cur' in locals():
          cur.close()
      if 'conn' in locals():
          conn.close()

def get_severity_data():
    conn = get_snowflake_connection()
    if conn is None:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails

    try:
        query = """
        SELECT 
            SEVERITY, 
            COUNT(*) AS COUNT 
        FROM TICKETS_DETAILS_DYNAMIC 
        GROUP BY SEVERITY
        """
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()


def get_incident_data():
    conn = get_snowflake_connection()
    if conn is None:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails

    try:
        query = """
        SELECT 
            INCIDENT, 
            COUNT(*) AS OCCURRENCE 
        FROM VEHICLE_DETAILS_DYNAMIC 
        GROUP BY INCIDENT
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching incident data: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    finally:
        conn.close()


def Events_Dashboard():
  data, total_vehicles, ticket_df = get_snowflake_data()  # Update to receive all three values
  total, critical, severe, high, low, non_critical = get_security_event_status()  # Fetch security event status
  severity_df = get_severity_data()  # Fetch severity data for the pie chart

  st.title("Vehicle Security Events Management Dashboard")
  st.markdown('<style> div.block-container{padding-top:1rem;} </style>', unsafe_allow_html=True)
  st.markdown('### Territory Wise Count Metrics')

  col1, col2 = st.columns((1.5, 3.5))
  with col1:
      st.metric("Total Vehicles", f"{total_vehicles}")

  with col2:
      subcol1, subcol2 = st.columns(2)
      subcol1.metric("England", f"{data.get('England', {}).get('total_count', 0)}")
      subcol2.metric("Europe", f"{data.get('Europe', {}).get('total_count', 0)}")
      subcol1.metric("North America", f"{data.get('North America', {}).get('total_count', 0)}")
      subcol2.metric("South America", f"{data.get('South America', {}).get('total_count', 0)}")

  st.markdown('---')

  chart_col1, chart_col2 = st.columns((3.5, 3.5))
  with chart_col1:
      st.markdown('### Ticket Status')
      
      # Create a dropdown for selecting the year
      years = ticket_df['YEAR'].unique()  # Use ticket_df for years
      selected_year = st.selectbox('Select Year', years, key="donut_year")

      # Filter data for the selected year
      year_data = ticket_df[ticket_df['YEAR'] == selected_year]

      # Create a donut chart using Plotly
      fig = px.pie(
          year_data, 
          values='COUNT', 
          names='STATUS', 
          title=f'Ticket Status for {selected_year}', 
          hole=0.4
      )
      st.plotly_chart(fig)

  with chart_col2:
      st.markdown('### Tickets Info')
      subcol1, subcol2 = st.columns(2)
      subcol1.metric("Total Tickets", "900", "+8%")
      subcol2.metric("Open", "160", "+4%")
      subcol1.metric("In-Progress", "60", "+18%")
      subcol2.metric("Closed", "68", "+4%")
      st.markdown('### Closure Performance')
      
      perf_col1, perf_col2 = st.columns(2)
      perf_col1.metric("MTTR(Mean Time To Repair)", "165 Hrs", "+12 Hrs", "inverse")
      perf_col2.metric("MTBF (Mean Time Between Failures)", "700 Days", "-120 Days", "inverse")

  st.markdown('---')

  st.markdown('### Security Event Status')
  tcol1, tcol2, tcol3, tcol4, tcol5, tcol6 = st.columns(6)
  tcol1.metric("Total", total, "", "off")
  tcol2.metric("Critical", critical, "")
  tcol3.metric("Severe", severe, "")
  tcol4.metric("High", high, "")
  tcol5.metric("Low", low, "")
  tcol6.metric("Non-Critical", non_critical, "")

  col3, col4 = st.columns((3.5, 5))
 # Add the pie chart for severity
  #st.markdown('### Severity Distribution')
  
  with col3:
    with st.expander('About', expanded=True):
        st.write('''
            - :orange[**Critical**]: Immediate action required; a breach is actively compromising sensitive data or systems.
            - :orange[**Severe**]: Significant threat detected; urgent response needed to prevent escalation and mitigate damage.
            - :orange[**High**]: Serious risk identified; prompt investigation and remediation are necessary to protect assets.
            - :orange[**Low**]: Minor issues present; monitoring is advised, but no immediate action is required.
            - :orange[**Non-Critical**]: Minimal impact; routine checks and maintenance are sufficient to ensure ongoing security.
            ''')
        
  with col4:
    
    if not severity_df.empty:
        fig_severity = px.pie(
            severity_df, 
            values='COUNT', 
            names='SEVERITY', 
            title='Severity Distribution of Security Events'
        )
        st.plotly_chart(fig_severity)
    else:
        st.warning("No severity data available.")
        
    
        
    st.markdown('---')
# Data for the incidents
    incidents = [
        'Malware', 'DoS', 'Key Jacking', 'Network Sniffing', 
        'Ransomware', 'Brute Force', 'CAN Stroking', 
        'Buffer Overflow', 'RF Key Cracking'
    ]

    
    incident_counts = [50, 30, 10, 5, 20, 15, 2, 3, 1]

    # Calculate cumulative percentage
    total_incidents = sum(incident_counts)
    cumulative_counts = [sum(incident_counts[:i+1]) for i in range(len(incident_counts))]
    cumulative_percentage = [count / total_incidents * 100 for count in cumulative_counts]

    
    plt.figure(figsize=(10, 6))
    plt.bar(incidents, incident_counts, color='skyblue', label='Incident Counts')
    plt.plot(incidents, cumulative_percentage, color='orange', marker='o', label='Cumulative Percentage')
    plt.axhline(80, color='red', linestyle='--', label='80% Threshold')
    plt.title('Pareto Analysis Chart of Cyber Incidents')
    plt.xlabel('Incident Type')
    plt.ylabel('Number of Incidents')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis='y')

    # Show the plot in Streamlit
    st.pyplot(plt)

   


def Search_Page():
  st.subheader("Diagnostic Search Page")
  st.markdown('<style> div.block-container{padding-top:2rem;} </style>', unsafe_allow_html=True)

  search_input = st.text_input("Enter a VIN Number to search:")
  if st.button("Search"):
      if search_input:
          query = f"""
              SELECT *
              FROM VOC_DASH_DUMMY_DB.VOC_VEHICLE.VEHICLE_DETAILS_DYNAMIC
              WHERE VIN_NUMBER = '{search_input}'
          """
          vehicle_data = execute_snowflake_query(query)

          if not vehicle_data.empty:
              display_info(search_input, vehicle_data)
          else:
              st.warning("No data found for the given VIN number.")
      else:
          st.warning("Please enter a value to search.")

def display_info(value, data):
  vehicle_info = data.iloc[0]

  st.title("Vehicle Diagnostic Dashboard")
  st.markdown(f"### Vehicle ID: {value}")

  col1, col2 = st.columns(2)
  with col1:
      fig_speed = go.Figure(go.Indicator(
          mode="gauge+number",
          value=vehicle_info.get('CURRENT_SPEED', 0),
          domain={'x': [0, 1], 'y': [0, 1]},
          title={'text': "Current Speed (km/h)"},
          gauge={'axis': {'range': [0, 300]},
                 'bar': {'color': "#1f77b4"},
                 'steps': [
                     {'range': [0, 100], 'color': "lightgray"},
                     {'range': [100, 200], 'color': "gray"},
                     {'range': [200, 300], 'color': "darkgray"}
                 ]}
      ))
      fig_speed.update_layout(height=300)
      st.plotly_chart(fig_speed, use_container_width=True)

  with col2:
      battery_remaining = vehicle_info['BATTERY_PERCENTAGE']
      battery_data = [battery_remaining, 100 - battery_remaining]
      battery_labels = ["Remaining", "Depleted"]
      fig_battery = go.Figure(go.Pie(
          labels=battery_labels,
          values=battery_data,
          hole=0.4,
          marker=dict(colors=["#2ecc71", "#e74c3c"])
      ))
      fig_battery.update_layout(
          title="Battery Status",
          height=300
      )
      st.plotly_chart(fig_battery, use_container_width=True)

  tab1, tab2, tab3 = st.tabs(["Basic Info", "System Status", "Sensor Data"])

  with tab1:
      col3, col4, col5 = st.columns(3)
      with col3:
          st.metric("VIN", value)
          st.metric("Location", vehicle_info['LOCATION'])
          st.metric("Total Mileage", f"{vehicle_info['TOTAL_MILEAGE']} km")
      with col4:
          st.metric("Engine Temperature", f"{vehicle_info['ENGINE_TEMPERATURE']}°C")
          st.metric("Battery Temperature", f"{vehicle_info['BATTERY_TEMPERATURE']}°C")
          st.metric("Ambient Temperature", f"{vehicle_info['AMBIENT_TEMPERATURE']}°C")
      with col5:
          st.metric("DTE", f"{vehicle_info['DISTANCE_TO_EMPTY']} km")
          st.metric("Door Status", vehicle_info['DOOR_STATUS'])
          st.metric("Brake Fluid", vehicle_info['BRAKE_FLUID_STATUS'])

  with tab2:
      st.subheader("Tire Pressure Status")
      tire_pressure = {
          "Front Left (FL)": vehicle_info['TIRE_PRESSURE_FL'],
          "Front Right (FR)": vehicle_info['TIRE_PRESSURE_FR'],
          "Rear Left (RL)": vehicle_info['TIRE_PRESSURE_RL'],
          "Rear Right (RR)": vehicle_info['TIRE_PRESSURE_RR']
      }

      fig_tire = go.Figure(go.Bar(
          x=list(tire_pressure.keys()),
          y=list(tire_pressure.values()),
          text=list(tire_pressure.values()),
          textposition='auto',
          marker_color=['#2ecc71', '#2ecc71', '#e74c3c', '#2ecc71']
      ))
      fig_tire.update_layout(
          title="Tire Pressure (PSI)",
          xaxis_title="Tires",
          yaxis_title="Pressure (PSI)",
          height=400
      )
      st.plotly_chart(fig_tire, use_container_width=True)

      st.subheader("ADAS Sensor Status")
      col6, col7, col8 = st.columns(3)
      with col6:
          st.success("Radar: Functional" if vehicle_info['ADAS_SENSOR_RADAR'] == 'Functional' else "Radar: Error")
      with col7:
          st.success("Camera: Functional" if vehicle_info['ADAS_SENSOR_CAMERA'] == 'Functional' else "Camera: Error")
      with col8:
          st.success("LiDAR: Functional" if vehicle_info['ADAS_SENSOR_LIDAR'] == 'Functional' else "LiDAR: Error")

  with tab3:
      st.subheader("Engine Temperature (Last 24 hours)")
      time = np.arange(0, 24, 1)
      engine_temp = vehicle_info['ENGINE_TEMPERATURE'] + 5 * np.sin(np.pi * time / 12)

      fig_temp = go.Figure()
      fig_temp.add_trace(go.Scatter(
          x=time,
          y=engine_temp,
          mode='lines+markers',
          name='Temperature',
          line=dict(color='#1f77b4', width=2)
      ))
      fig_temp.update_layout(
          xaxis_title="Hour",
          yaxis_title="Temperature (°C)",
          height=400
      )
      st.plotly_chart(fig_temp, use_container_width=True)

      st.subheader("System Status")
      col9, col10 = st.columns(2)
      with col9:
          st.metric("ABS Status", "Active" if vehicle_info['ABS_ACTIVE'] else "Inactive", "Normal")
      with col10:
          st.metric("Brake System", vehicle_info['BRAKE_FLUID_STATUS'], "Normal")

if __name__ == "__main__":
  main()
