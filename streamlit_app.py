#import sys
import os
import streamlit as st


import requests
import pandas as pd
import plost
import time
import math
import plotly.express as px
import plotly.graph_objects as go
import folium
import matplotlib.pyplot as plt
import re
import numpy as np
from urllib.parse import quote_plus


st.set_page_config(page_title="VOC αlpha - JLR", layout='wide', initial_sidebar_state='expanded', page_icon="JLR_Blue_Logo.svg")



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

# Use the custom CSS class
#st.markdown('<div class="custom-container"><h2>Custom Styled Container</h2><p>This container uses custom CSS.</p></div>', unsafe_allow_html=True)

# Display messages
#st.warning("This is a warning message.")
#st.info("This is an informative message.")
#st.success("Database Synchronization Successful!")
#st.error("An error occurred. Please try again.")

# Load sample data
seattle_weather = pd.read_csv('https://raw.githubusercontent.com/tvst/plost/master/data/seattle-weather.csv', parse_dates=['date'])
stocks = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/stocks_toy.csv')

# Define the main function
def main():
  # Define pages and their associated functions
  pages = {
      "Security Dashboard": Events_Dashboard,
      "Diagnostic Search": Search_Page,
  }

  with st.sidebar:
      # Sidebar header
      st.markdown('<div class="title-container"><h1>Jaguar Land Rover αlpha</h1></div>', unsafe_allow_html=True)
      
      # Initialize session state for selected page if it doesn't exist
      if 'selected_page' not in st.session_state:
          st.session_state.selected_page = "Security Dashboard"

      # Navigation using selectbox
      st.session_state.selected_page = st.selectbox(
          "Navigate to",
          list(pages.keys()),
          index=list(pages.keys()).index(st.session_state.selected_page),
          label_visibility="collapsed"
      )

      # Separator between navigation and tools
      
      st.divider()
      
      # Tools section
      st.header("Action Center")
      
      # Footer links container
      with st.container():
          # Create columns for tool buttons
          col1, col2 = st.columns(2)
          
          with col1:
              st.button("War Room", use_container_width=True)
              st.button("Attack", use_container_width=True)
          
          with col2:
              st.button("Health Check", use_container_width=True)
              st.button("Defence", use_container_width=True)
               
               # Footer
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
  
  # Display the selected page content
  page_function = pages[st.session_state.selected_page]
  page_function()
  
  st.markdown('---')




# Add custom CSS to style the links
st.markdown("""
  <style>
  .nav-link:hover {
      background-color: rgba(255, 255, 255, 0.1);
      padding: 5px;
      border-radius: 4px;
  }
  </style>
""", unsafe_allow_html=True)


def Events_Dashboard():
    # Header
    st.title("Vehicle Security Events Management Dashboard")
    st.markdown('<style> div.block-container{padding-top:1rem;} </style>', unsafe_allow_html=True)
    st.markdown('### Territory Wise Count Metrics')
    # Metrics Section
    #st.markdown('### Metrics')
    
    # Create two main columns for metrics
    col1, col2 = st.columns((1.5, 3.5))

    # Left column - Vehicle count
    with col1:
        col1.metric("Total Vehicles", "70", "12")
   
    
    # Right column - Geographic metrics in 2x2 grid
    with col2:
        #st.markdown('### Territory Wise Count')
        subcol1, subcol2 = st.columns(2)
        
        # First row
        with subcol1:
            st.metric("England", "900", "+8%")
        with subcol2:
            st.metric("Europe", "860", "+4%")
        
        # Second row
        with subcol1:
            st.metric("North America", "921", "+18%")
        with subcol2:
            st.metric("South America", "186", "+4%")

    st.markdown('---')

    # Charts Section
    chart_col1, chart_col2 = st.columns((3.5, 3.5))

    # Left chart column
    with chart_col1:
        st.markdown('### Reported Events')
        donut_theta = st.selectbox('Select Year', ('q2', 'q3'), key="donut_theta")
        plost.donut_chart(
            data=stocks,
            theta=donut_theta,
            color='company',
            legend='bottom',
            use_container_width=True
        )
        
        # European Population Pie Chart
        df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
        df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries'
        fig = px.pie(df, values='pop', names='country', title='Population of European continent')
        st.plotly_chart(fig)

    # Right chart column
    with chart_col2:
        st.markdown('### Events Info')
        
        #st.markdown('### Territory Wise Count')
        subcol1, subcol2 = st.columns(2)
        
        # First row
        with subcol1:
            st.metric("Total Events", "900", "+8%")
        with subcol2:
            st.metric("Open", "860", "+4%")
        
        # Second row
        with subcol1:
            st.metric("In-Progress", "921", "+18%")
        with subcol2:
            st.metric("Closed", "186", "+4%")

    st.markdown('---')

    # Bottom Section
    bottom_col1, bottom_col2 = st.columns((5, 5))

    # Ticket Status Section
    with bottom_col1:
        st.markdown('### Ticket Status')
        
        # Ticket metrics in row
        tcol1, tcol2, tcol3, tcol4 = st.columns(4)
        tcol1.metric("Total", "165", "", "off")
        tcol2.metric("Open", "70", "12")
        tcol3.metric("In Progress", "9", "-8")
        tcol4.metric("Closed", "86", "4")

        # Ticket Status Pie Chart
        labels = ['Open', 'In Progress', 'Closed']
        sizes = [15, 30, 45]
        colors = ['#ff9999','#66b3ff','#99ff99']
        explode = (0.1, 0, 0)
        
        plt.figure(figsize=(3, 3))
        plt.pie(sizes, 
                explode=explode, 
                labels=labels, 
                colors=colors, 
                autopct='%1.1f%%', 
                shadow=True, 
                startangle=140)
        plt.axis('equal')
        st.pyplot(plt)

    # Performance Metrics Section
    with bottom_col2:
        st.markdown('### Closure Performance')
        
        # Performance metrics in row
        perf_col1, perf_col2 = st.columns(2)
        perf_col1.metric("MTTR(Mean Time To Repair)", "165 Hrs", "+12 Hrs", "inverse")
        perf_col2.metric("MTBF (Mean Time Between Failures)", "700 Days", "-120 Days", "inverse")

        # Performance Chart
        plot_data = st.multiselect('Select data', 
                                  ['temp_min', 'temp_max'], 
                                  ['temp_min', 'temp_max'])
        plot_height = st.slider('Specify plot height', 200, 500, 250)
        if plot_data:
            st.line_chart(seattle_weather[plot_data], height=plot_height)

def execute_snowflake_query(query):
  import snowflake.connector
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
      df = pd.DataFrame(results, columns=columns)
      return df
      
  except Exception as e:
      st.error(f"Database connection error: {str(e)}")
      return pd.DataFrame()
      
  finally:
      if 'cur' in locals():
          try:
              cur.close()
          except:
              pass
      if 'conn' in locals():
          try:
              conn.close()
          except:
              pass

def Search_Page():
  st.subheader("Diagnostic Search Page")
  st.markdown('<style> div.block-container{padding-top:2rem;} </style>', unsafe_allow_html=True)

  search_input = st.text_input("Enter a VIN Number to search:")
  if st.button("Search"):
      if search_input:
          try:
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
              
          except Exception as e:
              st.error(f"An error occurred: {str(e)}")
      else:
          st.warning("Please enter a value to search.")

def display_info(value, data):
  # Extract data from the DataFrame (first row since we're querying by VIN)
  vehicle_info = data.iloc[0]
  
  # Main Header with Vehicle Info
  st.title("Vehicle Diagnostic Dashboard")
  st.markdown(f"### Vehicle ID: {value}")
  
  # Create two columns for key metrics
  col1, col2 = st.columns(2)
  
  # Column 1: Speedometer (assuming current speed is calculated or available)
  with col1:
      fig_speed = go.Figure(go.Indicator(
          mode="gauge+number",
          value=vehicle_info['CURRENT_SPEED'] if 'CURRENT_SPEED' in vehicle_info else 0,
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

  # Column 2: Battery Status
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

  # Create tabs for different categories of information
  tab1, tab2, tab3 = st.tabs(["Basic Info", "System Status", "Sensor Data"])

  # Tab 1: Basic Vehicle Information
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

  # Tab 2: System Status
  with tab2:
      # Tire Pressure Visualization
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

      # ADAS Status
      st.subheader("ADAS Sensor Status")
      col6, col7, col8 = st.columns(3)
      
      with col6:
          if vehicle_info['ADAS_SENSOR_RADAR'] == 'Functional':
              st.success("Radar: Functional")
          else:
              st.error("Radar: Error")
      with col7:
          if vehicle_info['ADAS_SENSOR_CAMERA'] == 'Functional':
              st.success("Camera: Functional")
          else:
              st.error("Camera: Error")
      with col8:
          if vehicle_info['ADAS_SENSOR_LIDAR'] == 'Functional':
              st.success("LiDAR: Functional")
          else:
              st.error("LiDAR: Error")

  # Tab 3: Sensor Data
  with tab3:
      # Engine Temperature Over Time (You might want to fetch historical data from another table)
      st.subheader("Engine Temperature (Last 24 hours)")
      # This part would need historical data from the database
      # For now, using dummy data
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

      # ABS and Brake System Status
      st.subheader("System Status")
      col9, col10 = st.columns(2)
      
      with col9:
          st.metric("ABS Status", "Active" if vehicle_info['ABS_ACTIVE'] else "Inactive", "Normal")
      with col10:
          st.metric("Brake System", vehicle_info['BRAKE_FLUID_STATUS'], "Normal")

if __name__ == "__main__":
    main()
