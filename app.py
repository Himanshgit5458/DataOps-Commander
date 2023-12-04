import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as pt


def main():
    st.sidebar.title("Sidebar")
    selected_option = st.sidebar.radio("Select Option", ["About","SM Bifurcation", "Lead Qualification","Lead Analytics" ])
    st.sidebar.info(f"You selected: {selected_option}")

    if selected_option=="About":
        st.title("DataOps Commander")
        st.write("DataOps Commander is your compass in the realm of data operations, providing a robust and efficient solution for orchestrating seamless data workflows.")


    if selected_option=="SM Bifurcation":

        st.header("SM Bifurcation")
        st.header("Import Excel File")
        
        # File uploader for Excel file
        excel_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

        if excel_file is not None:
            # Read the Excel file
            df = pd.read_excel(excel_file)
            df['UniqueEntries'] = df.apply(lambda row: list(set(row[['SM1', 'SM2', 'SM3']])), axis=1)
            new_df=df[['Manager', 'Actual Lead Project Name',"UniqueEntries"]]
            new_df=new_df.explode('UniqueEntries', ignore_index=True)
            new_df=new_df[new_df['UniqueEntries'] != np.nan]
            new_df['UniqueEntries'] = new_df['UniqueEntries'].str.strip()
            new_df=new_df.dropna()
            # st.download_button(
            #  "Press to Download",
            #  new_df.to_csv(index=False).encode('utf-8'),
            #  "file.csv",
            # "text/csv",
            # key='download-csv'
            #  )

            st.write(new_df)

    if selected_option=="Lead Qualification":

        st.header("Lead Qualification")
    
        st.header("Upload Multiple Excel Files")
        excel_files = st.file_uploader("Upload Excel Files", type=["csv"], accept_multiple_files=True)
        dfs=[]
        dict={
            0: 'Ayush Singh',
            1: 'Gaurav Jain',
            2: 'Sha Thomas',
            3: 'Rajiv Raman',
            4: 'Diana Gomez',
            5: 'Arun Kumar',
            6: 'Deepak Bhati',
            7: 'Ashish Jaiswal'
        }

        for i, excel_file in enumerate(excel_files):
            df = pd.read_csv(excel_file)

            # Add a new column with a constant value based on the dictionary
            df['Sales Head'] = dict[i]
            dfs.append(df)
        if len(dfs)>0:
            concatenated_df = pd.concat(dfs, ignore_index=True)
            st.write(concatenated_df)
        else:
            pass

    if selected_option=="Lead Analytics":
        st.header("Lead Analysis")
        st.header("Import Excel File")

        

                
        # File uploader for Excel file
        excel_file = st.file_uploader("Upload Excel File", type=["csv"])

        if excel_file is not None:
            # Read the Excel file
            df = pd.read_csv(excel_file)
            cols=["Project Name","Assigned To","Lead Status","Source","Visited","Dead Reason","City","Created At" ]
            df=df[cols]
            df["Visited"] = df["Visited"].apply(lambda x: 1 if x == "Yes" else 0)

            df['Created At'] = pd.to_datetime(df['Created At'], format='%d-%m-%Y %I:%M:%S %p', errors='coerce')
            df['Created At'] = df['Created At'].combine_first(pd.to_datetime(df['Created At'], format='%d-%m-%Y', errors='coerce'))

            # Extract day, month, and year
            df['Day'] = df['Created At'].dt.day
            df['Month'] = df['Created At'].dt.month
            df['Year'] = df['Created At'].dt.year


            df.drop(["Created At"],axis=1,inplace=True)
            df["count"]=1
            df["Quality"]=np.where(
    (df['Lead Status'].isin(['Fake', 'Broker'])) | ((df['Lead Status'] == 'Dead') & (df['Dead Reason'].isin(['Continuously Not Contactable', 'Not Looking for property']))),
    0,
    1
)
            # Overall

            st.title("Overall Analysis")


            overall_marketing=pd.concat([df.groupby(["Source"])["Visited"].sum(),df.groupby(["Source"])["count"].sum(), df["Source"].value_counts(normalize=True)*100, df.groupby(["Source"])["Quality"].mean()*100], axis=1, sort=False)
            overall_marketing.columns=["Visited","Lead Count","Proportion","Quality %"]

            overall_marketing["Qualified"]=round(overall_marketing["Quality %"]*overall_marketing["Lead Count"]/100,1)

            # Assuming combined_series is your DataFrame
            overall_marketing["QL/SV"] = np.where(
                (overall_marketing["Visited"] != 0),
                round(overall_marketing["Qualified"] / overall_marketing["Visited"], 1),
                "No Visits"
            )

            # Replace 0/0 by "No Qualified leads"
            overall_marketing["QL/SV"] = np.where(
                (overall_marketing["Qualified"] == 0) & (overall_marketing["Visited"] == 0),
                "No Qualified leads",
                overall_marketing["QL/SV"]
            )
            
            # overall_sales=pd.concat([df.groupby(["Assigned To"])["count"].sum(),df.groupby(["Assigned To"])["Visited"].sum(),df.groupby(["Assigned To"])["Quality"].mean()*100], axis=1, sort=False)
            
            combined_series = pd.concat([df.groupby(["Assigned To"])["count"].sum(),df.groupby(["Assigned To"])["Visited"].sum(),round(df.groupby(["Assigned To"])["Quality"].mean()*100,1)], axis=1, sort=False)
            combined_series["Qualified"]=round(combined_series["Quality"]*combined_series["count"]/100,1)

            # Assuming combined_series is your DataFrame
            combined_series["QL/SV"] = np.where(
                (combined_series["Visited"] != 0),
                round(combined_series["Qualified"] / combined_series["Visited"], 1),
                "No Visits"
            )

            # Replace 0/0 by "No Qualified leads"
            combined_series["QL/SV"] = np.where(
                (combined_series["Qualified"] == 0) & (combined_series["Visited"] == 0),
                "No Qualified leads",
                combined_series["QL/SV"]
            )

            combined_series.columns=["Lead Count","No. of Visits","Quality %","No. of Qualified Leads","Qualified Leads per site visits"]
                        
            
            st.write(overall_marketing)
            st.write(combined_series)

            

            st.title("Filtered Analysis")

            Day, Month, Year, city = st.columns(4)
            name, POC = st.columns(2)
            Source, status = st.columns(2)

            month_input = Month.selectbox("Month", ["ALL"] + np.unique(df["Month"]).tolist(), key="month_input")
            year_input = Year.selectbox("Year", ["ALL"] + np.unique(df["Year"]).tolist(), key="year_input")
            name_input = name.selectbox("Name", ["ALL"] + np.unique(df["Project Name"]).tolist(), key="name_input")
            poc_input = POC.selectbox("POC", ["ALL"] + np.unique(df["Assigned To"]).tolist(), key="poc_input")
            source_input = Source.selectbox("Source", ["ALL"] + np.unique(df["Source"]).tolist(), key="source_input")
            status_input = status.selectbox("Status", ["ALL"] + np.unique(df["Lead Status"]).tolist(), key="status_input")
            city_input = city.selectbox("City", ["ALL"] + np.unique(df["City"]).tolist(), key="city_input")
            selected_day = Day.selectbox("Select Day", ["ALL"] + np.unique(df["Day"]).tolist(), key="day_input")

            fd=df.copy()

            if month_input!="ALL":
                fd=fd[fd["Month"]==month_input]

            if year_input != "ALL":
                fd = fd[fd["Year"] == year_input]

            if name_input != "ALL":
                fd = fd[fd["Project Name"] == name_input]

            if poc_input != "ALL":
                fd = fd[fd["Assigned To"] == poc_input]

            if source_input != "ALL":
                fd = fd[fd["Source"] == source_input]

            if status_input != "ALL":
                fd = fd[fd["Lead Status"] == status_input]

            if city_input != "ALL":
                fd = fd[fd["City"] == city_input]

            if selected_day != "ALL":
                fd = fd[fd["Day"] == selected_day]





            # Overall
            overall_marketing2=pd.concat([fd.groupby(["Source"])["Visited"].sum(),fd.groupby(["Source"])["count"].sum(), fd["Source"].value_counts(normalize=True)*100, fd.groupby(["Source"])["Quality"].mean()*100], axis=1, sort=False)
            overall_marketing2.columns=["Visited","Lead Count","Proportion","Quality %"]
            
            # overall_sales=pd.concat([df.groupby(["Assigned To"])["count"].sum(),df.groupby(["Assigned To"])["Visited"].sum(),df.groupby(["Assigned To"])["Quality"].mean()*100], axis=1, sort=False)
            
            combined_series = pd.concat([fd.groupby(["Assigned To"])["count"].sum(),fd.groupby(["Assigned To"])["Visited"].sum(),round(fd.groupby(["Assigned To"])["Quality"].mean()*100,1)], axis=1, sort=False)
            combined_series["Qualified"]=round(combined_series["Quality"]*combined_series["count"]/100,1)

            # Assuming combined_series is your DataFrame
            combined_series["QL/SV"] = np.where(
                (combined_series["Visited"] != 0),
                round(combined_series["Qualified"] / combined_series["Visited"], 1),
                "No Visits"
            )

            # Replace 0/0 by "No Qualified leads"
            combined_series["QL/SV"] = np.where(
                (combined_series["Qualified"] == 0) & (combined_series["Visited"] == 0),
                "No Qualified leads",
                combined_series["QL/SV"]
            )

            combined_series.columns=["Lead Count","No. of Visits","Quality %","No. of Qualified Leads","Qualified Leads per site visits"]
                        
            
            st.write(overall_marketing2)
            st.write(combined_series)
            

if __name__ == "__main__":
    main()

