import streamlit as st
import pandas as pd
import os
from io import BytesIO
import plotly.express as px  

# Set up our App
st.set_page_config(page_title="💽 Data Sweeper", layout="wide")
st.title("💽 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# Sidebar Message
with st.sidebar:
    st.subheader("📂 Upload Your Files")
    st.write("Upload your CSV or Excel file to start processing and exploring data.")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display file info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")
        
        # Preview Data
        st.write("🔎 Preview the Dataframe")
        st.dataframe(df.head())
        
        # Sidebar for Data Cleaning Options
        with st.sidebar:
            st.subheader("🛠️ Data Cleaning Options")
            
            # Standardize Column Names
            if st.checkbox(f"Standardize Column Names ({file.name})"):
                df.columns = [col.lower().replace(" ", "_") for col in df.columns]
                st.write("Column names standardized!")
            
            # Remove Duplicates
            if st.button(f"Remove Duplicates ({file.name})"):
                df.drop_duplicates(inplace=True)
                st.write("Duplicates removed!")

            # Fill Missing Values
            fill_method = st.radio(f"Fill Missing Values for {file.name}", ["Mean", "Median", "Mode"], key=f"fill_{file.name}")
            if st.button(f"Apply Missing Value Fix ({file.name})"):
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if fill_method == "Mean":
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                elif fill_method == "Median":
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
                elif fill_method == "Mode":
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mode().iloc[0])
                st.write(f"Missing values filled using {fill_method}!")

            # Remove Outliers
            if st.button(f"Remove Outliers ({file.name})"):
                numeric_cols = df.select_dtypes(include=["number"])  
                Q1 = numeric_cols.quantile(0.25)
                Q3 = numeric_cols.quantile(0.75)
                IQR = Q3 - Q1
                df = df[~((numeric_cols < (Q1 - 1.5 * IQR)) | (numeric_cols > (Q3 + 1.5 * IQR))).any(axis=1)]
                st.write("Outliers removed!")
        
        # Select Columns to Keep
        st.subheader("🎯 Select Columns to Keep")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]
        
        # Data Visualization
        st.subheader("📊 Data Visualization")
        viz_type = st.selectbox(f"Choose Visualization Type for {file.name}", ["Bar Chart", "Pie Chart", "Scatter Plot", "Histogram"])
        
        if st.button(f"Generate {viz_type} ({file.name})"):
            if viz_type == "Bar Chart":
                st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])
            elif viz_type == "Pie Chart":
                pie_col = st.selectbox("Select Column for Pie Chart", df.columns)
                fig = px.pie(df, names=pie_col, title=f"Pie Chart of {pie_col}")
                st.plotly_chart(fig)
            elif viz_type == "Scatter Plot":
                num_cols = df.select_dtypes(include="number").columns
                x_col = st.selectbox("Select X-axis", num_cols)
                y_col = st.selectbox("Select Y-axis", num_cols)
                fig = px.scatter(df, x=x_col, y=y_col, title=f"Scatter Plot of {x_col} vs {y_col}")
                st.plotly_chart(fig)
            elif viz_type == "Histogram":
                hist_col = st.selectbox("Select Column for Histogram", df.select_dtypes(include="number").columns)
                fig = px.histogram(df, x=hist_col, title=f"Histogram of {hist_col}")
                st.plotly_chart(fig)
        
        # File Conversion & Download
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        new_file_name = st.text_input("Rename File Before Download", value=file.name.replace(file_ext, ""))
        
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_ext = ".csv"
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False)
                file_ext = ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"⬇️ Download {new_file_name}{file_ext}",
                data=buffer,
                file_name=f"{new_file_name}{file_ext}",
                mime=mime_type
            )

st.success("🎉 All files processed!")
